from typing import Any, TypedDict
class WeatherState(TypedDict, total=False):
    user_message: str
    history: list[dict[str, str]]
    activity_tag: str | None
    is_outdoor_activity: bool
    location_query: str | None
    time_ref: str
    resolved_location: dict[str, Any] | None
    weather: dict[str, Any] | None
    matched_sops: list[dict[str, Any]]
    primary_sop: dict[str, Any] | None
    response: str
    status: str
    error: str | None
