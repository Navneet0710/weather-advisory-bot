from pathlib import Path
import operator, yaml
OPS={">":operator.gt,">=":operator.ge,"<":operator.lt,"<=":operator.le,"==":operator.eq,"!=":operator.ne}
THUNDERSTORM_CODES={95,96,97,98,99}
def load_policies(path="policies/sops.yaml"):
    s=yaml.safe_load(Path(path).read_text(encoding="utf-8"))["sops"]
    if len(s)<10 or len({x["id"] for x in s})!=len(s): raise ValueError("Invalid SOP set")
    return s
def aggregate(weather,source,field,agg):
    vals=[v for v in weather.get(source,{}).get(field,[]) if v is not None]
    if not vals:return None
    if agg=="max":return max(vals)
    if agg=="min":return min(vals)
    if agg=="sum":return sum(vals)
    if agg=="mean":return sum(vals)/len(vals)
    if agg=="any_thunderstorm":return any(int(v) in THUNDERSTORM_CODES for v in vals)
    raise ValueError(f"Unknown aggregate {agg}")
def eval_condition(weather,c):
    actual=aggregate(weather,c["source"],c["field"],c["aggregate"])
    return False if actual is None else OPS[c["op"]](actual,c["value"])
def eval_group(weather,g):
    if "all" in g:return all(eval_condition(weather,c) for c in g["all"])
    if "any" in g:return any(eval_condition(weather,c) for c in g["any"])
    if "at_least" in g:return sum(eval_condition(weather,c) for c in g["at_least"]["of"])>=g["at_least"]["n"]
    raise ValueError("Unsupported condition group")
def evaluate_sop(weather,sop):
    if sop.get("type")=="rubric": return sum(eval_condition(weather,c) for c in sop["rubric"])>=sop["min_pass"]
    return eval_group(weather,sop["conditions"])
def match_sops(weather,sops,activity):
    out=[s for s in sops if s.get("scope")=="global" or activity in s.get("activities",[]) if evaluate_sop(weather,s)]
    return sorted(out,key=lambda s:(-int(s.get("priority",0)),-{"critical":4,"high":3,"caution":2,"info":1}.get(s.get("severity"),0)))
