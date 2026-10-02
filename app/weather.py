from datetime import datetime,timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import requests,yaml
GEO_URL="https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL="https://api.open-meteo.com/v1/forecast"
def geocode(city):
    r=requests.get(GEO_URL,params={"name":city,"count":1},timeout=10); r.raise_for_status()
    x=(r.json().get("results") or [None])[0]
    if not x: raise ValueError(f"Could not resolve location: {city}")
    return {"name":x.get("name",city),"country":x.get("country","") ,"latitude":x["latitude"],"longitude":x["longitude"],"timezone":x.get("timezone","UTC")}
def fetch_weather(location):
    f=yaml.safe_load(Path("policies/fields.yaml").read_text())
    p={"latitude":location["latitude"],"longitude":location["longitude"],"timezone":"auto","forecast_days":2,"current":",".join(f["current"]),"hourly":",".join(f["hourly"]),"daily":",".join(f["daily"])}
    r=requests.get(WEATHER_URL,params=p,timeout=15); r.raise_for_status(); d=r.json()
    if "hourly" not in d or "daily" not in d: raise ValueError("Incomplete weather payload")
    return d
def select_window(weather,time_ref):
    tz=weather.get("timezone","UTC"); now=datetime.now(ZoneInfo(tz)); ref=(time_ref or "today").lower()
    if "tomorrow" in ref: date=(now+timedelta(days=1)).date(); lo,hi=0,23
    elif "evening" in ref: date=now.date(); lo,hi=17,22
    elif "morning" in ref: date=now.date(); lo,hi=6,11
    else: date=now.date(); lo,hi=now.hour,23
    idx=[]
    for i,t in enumerate(weather["hourly"]["time"]):
        dt=datetime.fromisoformat(t).replace(tzinfo=ZoneInfo(tz))
        if dt.date()==date and lo<=dt.hour<=hi: idx.append(i)
    if not idx: idx=list(range(min(24,len(weather["hourly"]["time"]))))
    hourly={k:[v[i] for i in idx] if isinstance(v,list) else v for k,v in weather["hourly"].items()}
    return {"timezone":tz,"time_ref":time_ref,"hourly":hourly,"daily":weather["daily"],"raw":weather}
