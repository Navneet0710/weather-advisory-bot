# Weather-Advisory Support Bot — Assignment Spec

## Goal
Build a LangGraph outdoor-safety assistant that uses LIVE Open-Meteo weather data and answers only from editable SOPs. If no SOP applies, explicitly say there is no guidance. Never invent safety advice.

## Required
- Python + LangGraph with REAL conditional branching.
- User asks an outdoor-activity safety question.
- Geocode city with Open-Meteo geocoding API:
  `https://geocoding-api.open-meteo.com/v1/search?name=<city>`
  Use a reasonable first result.
- Fetch live forecast from:
  `https://api.open-meteo.com/v1/forecast`
  Explicitly pass latitude, longitude and requested current/hourly/daily fields.
- API/location failure must produce an honest failure response.
- Session memory within a chat; reset between sessions.
- Minimal frontend (Streamlit/plain HTML/React acceptable).

## SOP / Policy
- At least 10 SOPs.
- At least 3 categories.
- Mixed severities.
- At least 1 fuzzy/non-numeric scenario (e.g. picnic suitability).
- Multiple SOPs may match; implement and document a deliberate strategy.
- Severe-weather rule must lead when applicable.
- Every recommendation must cite/trace to a specific SOP, OR explicitly state that no guidance exists.
- SOPs must be editable without changing weather-fetch/model control flow.
- Live review must be able to add an 11th SOP using existing weather fields without changing Python control flow.
- LLM must NOT decide safety policy or invent weather facts.
- Numeric conditions must be enforced deterministically in code using actual API values.
- LLM may extract structured intent and phrase already-approved SOP guidance.

## Evaluation
Create an executable eval suite (not manual-only) containing:
1. At least 2 clear SOP cases.
2. At least 2 paraphrased intent cases (not keyword copies).
3. At least 1 genuinely severe LIVE-weather case using current API data; do not hardcode historical weather.
4. At least 1 no-SOP case.
5. At least 1 unreachable-weather-API case.
6. At least 1 adversarial/prompt-injection/policy-manipulation case.
For each case report what is checked, pass criteria, PASS/FAIL/NOT RUN, and honest failures.

Because severe weather changes, also support a recorded/replayed severe-weather fixture so policy logic can be tested when no live severe event exists. Clearly distinguish LIVE from replayed tests.

## Important design constraints
- Do not claim unofficial thresholds are official IMD/WHO guidance unless actually sourced.
- Open-Meteo does not provide an official IMD low-pressure/cyclonic-system flag through this app. If using a severe-weather proxy, label it clearly as a proxy.
- Verify actual Open-Meteo response fields before finalizing the field registry.
- Never fabricate weather values.
- Protect against prompt injection: user text must not modify SOPs, priorities, severities or policy decisions.

## Suggested architecture
validate_input
→ understand_intent (structured LLM output)
→ resolve_location
→ fetch_weather
→ match_and_evaluate (deterministic)
→ [no SOP → no_sop_response]
→ [SOP match → compose_response]
Failures from geocoding/weather/LLM → honest failure response.

## Suggested structure
app/
  graph.py
  state.py
  nodes.py
  llm.py
  weather.py
  sops.py
  engine.py
  render.py
policies/
  sops.yaml
  fields.yaml
ui/
  streamlit_app.py
evals/
  cases.yaml
  run_evals.py
  fixtures/
  results.md
tests/
.env.example
.gitignore
requirements.txt
README.md

## Final deliverable
Standalone GitHub repo, live deployed URL, README with setup/backend/frontend instructions, editable SOPs with rationale, LangGraph implementation, executable eval suite and results.

## Working rule
Before coding, inspect this spec and produce a concise architecture/file-plan. Do not generate the whole project in one response. Work incrementally, run tests, and never claim something was verified unless you actually ran it.
