def weather_summary(w):
    h=w.get("hourly",{}); out=[]
    for f in ["temperature_2m","precipitation_probability","precipitation","wind_speed_10m","wind_gusts_10m","uv_index"]:
        v=[x for x in h.get(f,[]) if x is not None]
        if v: out.append(f"{f}: {min(v):g}-{max(v):g}")
    return "; ".join(out)
def weather_block(w):
    h=w.get("hourly",{}); labels={"temperature_2m":"Temperature (°C)","precipitation_probability":"Precipitation probability (%)","precipitation":"Precipitation (mm)","wind_speed_10m":"Wind speed (km/h)","wind_gusts_10m":"Wind gust (km/h)","uv_index":"UV index"}; out=[]
    for f,l in labels.items():
        v=[x for x in h.get(f,[]) if x is not None]
        if v: out.append(f"- {l}: {min(v):g} to {max(v):g}")
    return "\n".join(out) or "- No requested weather values were available."
def final_response(loc,w,matches,advice,time_ref):
    if not matches:return f"I don't have guidance for that request under the policies configured for this bot. Location resolved to {loc['name']}, {loc['country']}."
    p=matches[0]; s=f"**{p['severity'].upper()} — {p['name']} ({p['id']})**\n{advice}\n\n**Weather used ({time_ref}):**\n{weather_block(w)}\n\n**Policy basis:** {p['id']} — {p['rationale']}"
    if len(matches)>1:s += "\n\n**Also applies:** "+", ".join(f"{x['id']} ({x['name']})" for x in matches[1:])
    return s
