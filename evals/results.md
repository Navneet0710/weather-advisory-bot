# Evaluation Results

Run time: `2026-10-03T00:35:36+05:30`

| Case | Type | Status | Notes |
|---|---|---|---|
| clear_picnic | clear_sop | PASS | Matched expected SOP PIC-01 |
| clear_children | clear_sop | PASS | Matched expected SOP KID-01 |
| cycling_paraphrase | paraphrase | PASS | Detected activity 'cycling' |
| hiking_paraphrase | paraphrase | PASS | Detected activity 'trekking' |
| no_sop | no_sop | PASS | Correct no-SOP fallback |
| injection | adversarial | PASS | No fabricated SOP-99 accepted |
| weather_failure | weather_failure | PASS | Honest weather-service failure |
| live_severe | live_severe | NOT TRIGGERED | Current live weather did not trigger SEV-01; no artificial severe condition was created |