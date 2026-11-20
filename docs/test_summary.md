# Test summary

**Automated:** 27 pytest tests passing (rules boundaries, each check, message composition,
AI safety fallback, API flow, role access, edge cases).

**Edge cases tested:** age exactly 45; document expiring today; wrong document in a slot; upload after decision;
unrequired slot; invalid age (15); AI rewrite drops an issue → fallback; AI service error → fallback;
underwriter dismisses all flags.

**Simulation (10 synthetic cases, `scripts/simulate.py`):**
Baseline 11 rounds total (avg 1.1) vs ClearPath 7 (avg 0.7). Biggest gain: case missing 4 documents (4 → 1).

**What didn't work / learned:**
- Strict name matching flags "Priya R. Sharma" — false positive; kept strict deliberately, human dismisses. Next: fuzzy match with confidence.
- Simulation is optimistic (assumes fixes are correct) — real benefit unproven.
- No measure yet of message clarity — needs user testing.
