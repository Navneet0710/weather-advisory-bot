from app.sops import evaluate_sop

def w():return {"hourly":{"temperature_2m":[38,37],"precipitation":[0,0],"precipitation_probability":[10,10],"wind_speed_10m":[15,15],"wind_gusts_10m":[20,20],"weather_code":[0,0],"uv_index":[9,9]},"daily":{"precipitation_sum":[80,20],"precipitation_probability_max":[80,20],"wind_gusts_10m_max":[25,25]}}
def test_heat():
    s={"conditions":{"all":[{"field":"temperature_2m","source":"hourly","aggregate":"max","op":">=","value":36}]}}
    assert evaluate_sop(w(),s)
def test_severe():
    s={"conditions":{"at_least":{"n":2,"of":[{"field":"precipitation_sum","source":"daily","aggregate":"max","op":">=","value":64.5},{"field":"precipitation_probability_max","source":"daily","aggregate":"max","op":">=","value":70}]}}}
    assert evaluate_sop(w(),s)
