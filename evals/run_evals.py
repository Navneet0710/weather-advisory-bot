from pathlib import Path
from datetime import datetime
import yaml

from app.graph import build_graph


def run_case(graph, case):
    return graph.invoke(
        {
            "user_message": case["query"],
            "history": [],
        }
    )


def sop_id(sop):
    return sop.get("id") if sop else None


def evaluate_case(case, result):
    case_type = case["type"]

    matched = result.get("matched_sops") or []
    matched_ids = [sop_id(s) for s in matched]
    response = result.get("response") or ""
    activity = result.get("activity_tag")

    if case_type == "clear_sop":
        expected = case["expected_sop"]

        if expected in matched_ids:
            return "PASS", f"Matched expected SOP {expected}"

        return "FAIL", f"Expected {expected}; matched {matched_ids or 'none'}"

    if case_type == "paraphrase":
        expected = case["expected_activity"]

        if activity == expected:
            return "PASS", f"Detected activity '{activity}'"

        return "FAIL", f"Expected '{expected}'; detected '{activity}'"

    if case_type == "no_sop":
        if not matched and "don't have guidance" in response.lower():
            return "PASS", "Correct no-SOP fallback"

        return "FAIL", f"Unexpected matches/response: {matched_ids}"

    if case_type == "adversarial":
        if "SOP-99" not in response and "SOP-99" not in str(matched_ids):
            return "PASS", "No fabricated SOP-99 accepted"

        return "FAIL", "Fabricated SOP-99 detected"

    if case_type == "weather_failure":
        if (
            result.get("status") == "done"
            and (
                "required service failed" in response.lower()
                or "without verified weather data" in response.lower()
            )
        ):
            return "PASS", "Honest weather-service failure"

        return "FAIL", "Weather failure was not handled honestly"

    if case_type == "live_severe":
        if "SEV-01" in matched_ids:
            return "PASS", "Live weather triggered SEV-01"

        return "NOT TRIGGERED", (
            "Current live weather did not trigger SEV-01; "
            "no artificial severe condition was created"
        )

    return "FAIL", f"Unknown case type: {case_type}"


def main():
    cases = yaml.safe_load(
        Path("evals/cases.yaml").read_text()
    )["cases"]

    graph = build_graph()
    results = []

    for case in cases:
        case_type = case["type"]

        try:
            if case_type == "weather_failure":
                import app.nodes as nodes

                original = nodes.fetch_weather

                def failing_weather(*args, **kwargs):
                    raise RuntimeError("Simulated weather API outage")

                nodes.fetch_weather = failing_weather

                try:
                    result = run_case(graph, case)
                finally:
                    nodes.fetch_weather = original
            else:
                result = run_case(graph, case)

            status, notes = evaluate_case(case, result)

        except Exception as exc:
            status = "ERROR"
            notes = f"{type(exc).__name__}: {exc}"

        results.append(
            {
                "id": case["id"],
                "type": case_type,
                "status": status,
                "notes": notes,
            }
        )

    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")

    lines = [
        "# Evaluation Results",
        "",
        f"Run time: `{timestamp}`",
        "",
        "| Case | Type | Status | Notes |",
        "|---|---|---|---|",
    ]

    for r in results:
        lines.append(
            f"| {r['id']} | {r['type']} | "
            f"{r['status']} | {r['notes']} |"
        )

    Path("evals/results.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print("\n".join(lines))
    print("\nSaved to evals/results.md")


if __name__ == "__main__":
    main()