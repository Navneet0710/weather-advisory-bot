from .state import WeatherState
from .sops import load_policies,match_sops
from .weather import geocode,fetch_weather,select_window
from .llm import extract_intent,compose_advice
from .render import weather_summary,final_response
SOPS=load_policies()
def validate_input(s): return {"status":"empty" if not s.get("user_message","").strip() else "ok"}
def understand(s):
    try:
        tags=sorted({a for x in SOPS for a in x.get("activities",[]) if a!="any"}); i=extract_intent(s["user_message"],s.get("history",[]),tags)
        return {"is_outdoor_activity":i.is_outdoor_activity,"activity_tag":i.activity_tag,"location_query":i.location,"time_ref":i.time_ref,"status":"ok"}
    except Exception as e:return {"status":"llm_error","error":str(e)}
def resolve_location(s):
    if not s.get("is_outdoor_activity"):return {"status":"no_sop"}
    if not s.get("location_query"):return {"status":"location_error","error":"No location was extracted."}
    try:return {"resolved_location":geocode(s["location_query"]),"status":"ok"}
    except Exception as e:return {"status":"location_error","error":str(e)}
def get_weather(s):
    try:return {"weather":select_window(fetch_weather(s["resolved_location"]),s.get("time_ref","today")),"status":"ok"}
    except Exception as e:return {"status":"weather_error","error":str(e)}
def evaluate(s):
    m=match_sops(s["weather"],SOPS,s.get("activity_tag","unknown"));return {"matched_sops":m,"primary_sop":m[0] if m else None,"status":"matched" if m else "no_sop"}
def compose(s):
    p=s["primary_sop"]; advice=compose_advice(p,s["resolved_location"]["name"],weather_summary(s["weather"]))
    return {"response":final_response(s["resolved_location"],s["weather"],s["matched_sops"],advice,s.get("time_ref","today")),"status":"done"}
def no_sop(s):return {"response":"I don't have guidance for that request under the policies configured for this bot.","status":"done"}
def failure(s):return {"response":f"I couldn't provide weather-based guidance because a required service failed: {s.get('error') or 'unknown error'}. I won't guess without verified weather data.","status":"done"}
