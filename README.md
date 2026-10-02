# Weather-Advisory Support Bot

LangGraph + live Open-Meteo + editable SOPs + Streamlit.

## Flow
validate_input → understand → resolve_location → get_weather → evaluate → compose.
Conditional branches handle empty input, LLM failure, location failure, weather failure, no-SOP and successful matches.

## Boundary
LLM: structured intent extraction and wording of already-approved SOP guidance.
Code: geocoding, weather retrieval, time-window slicing, SOP matching/evaluation, priority ordering and all displayed weather numbers.
YAML: policy source of truth.

## SOPs
12 SOPs are provided across cycling, outdoor exercise, children, elderly, pets, hiking, travel, recreation and a global severe-weather proxy. Add a new SOP using existing fields by editing `policies/sops.yaml`; no graph/control-flow change is required.

## Severe proxy
Open-Meteo does not provide an official IMD low-pressure/cyclonic-system flag in this app. SEV-01 is therefore a deterministic proxy, not an official classification. The 64.5 mm rainfall threshold matches the IMD lower bound for heavy rain; other proxy signals are explicit prototype policy choices.

## Setup (Windows PowerShell)

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Put your Gemini API key in `.env`.

## Run

```powershell
python -m pytest -q
streamlit run ui/streamlit_app.py
```

You do NOT run every Python file. `ui/streamlit_app.py` is the entry point and imports the graph and its modules.

## Eval

```powershell
python -m evals.run_evals.
```

Record actual PASS/FAIL/NOT RUN results in `evals/results.md`. The severe live case must remain dependent on the current API; do not hardcode historical weather.
