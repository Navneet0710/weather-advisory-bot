from langgraph.graph import StateGraph,START,END
from .state import WeatherState
from .nodes import validate_input,understand,resolve_location,get_weather,evaluate,compose,no_sop,failure
def rv(s):return "end" if s.get("status")=="empty" else "understand"
def ri(s):
    if s.get("status")=="llm_error":return "failure"
    return "no_sop" if not s.get("is_outdoor_activity") else "resolve_location"
def rl(s):return "failure" if s.get("status")=="location_error" else "get_weather"
def rw(s):return "failure" if s.get("status")=="weather_error" else "evaluate"
def re(s):return "no_sop" if s.get("status")=="no_sop" else "compose"
def build_graph():
    g=StateGraph(WeatherState)
    for n,f in [("validate_input",validate_input),("understand",understand),("resolve_location",resolve_location),("get_weather",get_weather),("evaluate",evaluate),("compose",compose),("no_sop",no_sop),("failure",failure)]:g.add_node(n,f)
    g.add_edge(START,"validate_input");g.add_conditional_edges("validate_input",rv,{"end":END,"understand":"understand"});g.add_conditional_edges("understand",ri,{"failure":"failure","no_sop":"no_sop","resolve_location":"resolve_location"});g.add_conditional_edges("resolve_location",rl,{"failure":"failure","get_weather":"get_weather"});g.add_conditional_edges("get_weather",rw,{"failure":"failure","evaluate":"evaluate"});g.add_conditional_edges("evaluate",re,{"no_sop":"no_sop","compose":"compose"})
    for n in ["compose","no_sop","failure"]:g.add_edge(n,END)
    return g.compile()
