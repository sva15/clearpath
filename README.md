# ClearPath — SafeLife Term-Life Onboarding (Hackathon Prototype)

**Team:** _<team name>_ · **Members:** _<names + GitHub handles>_

## Selected problem
When an underwriter needs more information from a term-life applicant, requests are vague or
arrive one at a time → repeated back-and-forth, weeks of delay, applicants drop off.
Details, evidence and labels: [`docs/problem.md`](docs/problem.md)

## Solution summary
**Ask once, clearly, check instantly.**
1. **Requirements engine** decides every needed document upfront (rules in `rules/term_life.yaml`).
2. **Instant checks** on upload: missing, wrong type, name mismatch, expired, too old, health contradiction.
3. **Underwriter console**: flags pre-filled; underwriter confirms/dismisses and sends **one combined request**.
4. **Applicant tracker**: status, what's missing and why, re-upload only flagged items.
A human makes every decision. Approval is blocked while issues are open.

## Tech stack
Python · FastAPI · SQLite · Streamlit · pytest · YAML rules

## Implemented vs simulated
| Implemented | Simulated |
|---|---|
| Rules engine, document checks, combined-request composer | Document reading (JSON stands in for OCR) |
| REST API, status flow, audit log | Login/roles (`X-Role` header) |
| Applicant + underwriter UI | Email (written to `outbox` table) |
| AI-rewrite safety check + fallback | AI service (off by default; no provider wired in) |

## Setup
```bash
python -m venv .venv && .venv\Scripts\activate      # Windows (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env                               # set CLEARPATH_TODAY=2026-11-20 for the demo data
set CLEARPATH_TODAY=2026-11-20
uvicorn backend.app.main:app --reload                # terminal 1 -> http://localhost:8000/docs
streamlit run frontend/app.py                        # terminal 2 -> http://localhost:8501
```

## Tests
```bash
python -m pytest -v          # 27 tests: rules, checks, messages/AI safety, API + edge cases
python scripts/simulate.py   # baseline vs ClearPath rounds on 10 synthetic cases
```

## Assumptions
- Fictional insurer *SafeLife*, individual term-life cover, online + agent channels. **(Assumption)**
- Thresholds (₹50L income proof, age 45 / ₹1Cr medical, 180-day reports, 90-day address) are illustrative, not real regulation. **(Assumption)**
- Bundling issues reduces rounds and drop-off. **(Hypothesis — simulated only)**

## Known limitations
- Name match is strict: "Priya R. Sharma" vs "Priya Sharma" is flagged (false positive → human dismisses).
- No real OCR, fraud, or medical-data validation; no real auth.
- Simulation assumes applicants fix everything correctly first time (optimistic).
- Single product; rules file supports more but not tested.
See [`docs/test_summary.md`](docs/test_summary.md).
