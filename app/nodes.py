import re 
from .state import WeatherState
from .sops import load_policies, match_sops
from .weather import geocode, fetch_weather, select_window
from .llm import extract_intent
from .render import weather_summary, final_response

SOPS = load_policies()


def validate_input(s):
    return {
        "status": "empty"
        if not s.get("user_message", "").strip()
        else "ok"
    }


def understand(s):
    try:
        tags = sorted({
            a
            for x in SOPS
            for a in x.get("activities", [])
            if a != "any"
        })

        i = extract_intent(
            s["user_message"],
            s.get("history", []),
            tags,
        )

        return {
            "is_outdoor_activity": i.is_outdoor_activity,
            "activity_tag": i.activity_tag,
            "location_query": i.location,
            "time_ref": i.time_ref,
            "status": "ok",
        }

    except Exception as e:
        return {
            "status": "llm_error",
            "error": str(e),
        }


def resolve_location(s):
    if not s.get("is_outdoor_activity"):
        return {"status": "no_sop"}

    if not s.get("location_query"):
        return {
            "status": "location_error",
            "error": "No location was extracted.",
        }

    try:
        return {
            "resolved_location": geocode(s["location_query"]),
            "status": "ok",
        }

    except Exception as e:
        return {
            "status": "location_error",
            "error": str(e),
        }


def get_weather(s):
    try:
        return {
            "weather": select_window(
                fetch_weather(s["resolved_location"]),
                s.get("time_ref", "today"),
            ),
            "status": "ok",
        }

    except Exception as e:
        return {
            "status": "weather_error",
            "error": str(e),
        }


def evaluate(s):
    matches = match_sops(
        s["weather"],
        SOPS,
        s.get("activity_tag", "unknown"),
    )

    return {
        "matched_sops": matches,
        "primary_sop": matches[0] if matches else None,
        "status": "matched" if matches else "no_sop",
    }


def compose(s):
    primary = s["primary_sop"]

    # Safety guidance comes directly from the approved SOP.
    advice = primary["guidance"]

    return {
        "response": final_response(
            s["resolved_location"],
            s["weather"],
            s["matched_sops"],
            advice,
            s.get("time_ref", "today"),
        ),
        "status": "done",
    }


def no_sop(s):
    activity = s.get("activity_tag", "unknown")
    message = s.get("user_message", "").lower()

    activity_sops = [
        sop
        for sop in SOPS
        if sop.get("scope") != "global"
        and activity in sop.get("activities", [])
    ]

    if not activity_sops:
        return {
            "response": (
                "I don't have guidance for that activity under the "
                "policies configured for this bot."
            ),
            "status": "done",
        }

    # Handle an explicit hypothetical wind-gust scenario.
    # This does NOT replace the verified live weather.
    if activity == "cycling":
        match = re.search(
            r"(?:wind\s+gusts?|gusts?).{0,30}?(\d+(?:\.\d+)?)\s*(?:km/?h|kph)",
            message,
        )

        if match:
            gust = float(match.group(1))
            wind_sop = next(
                (sop for sop in activity_sops if sop["id"] == "CYC-01"),
                None,
            )

            if wind_sop and gust >= 45:
                return {
                    "response": (
                        f"No. A wind gust of {gust:g} km/h meets the "
                        "CYC-01 cycling threshold of 45 km/h or higher. "
                        f"{wind_sop['guidance']}"
                    ),
                    "status": "done",
                }

    checked = ", ".join(sop["id"] for sop in activity_sops)
    summary = weather_summary(s["weather"])

    return {
        "response": (
            f"Yes — based on the verified weather, no configured "
            f"cycling warning is triggered for {s['resolved_location']['name']} "
            f"{s.get('time_ref', 'today')}. "
            f"Verified weather: {summary}. "
            f"SOPs checked: {checked}."
        ),
        "status": "done",
    }


def failure(s):
    return {
        "response": (
            "I couldn't provide weather-based guidance because a required "
            f"service failed: {s.get('error') or 'unknown error'}. "
            "I won't guess without verified weather data."
        ),
        "status": "done",
    }