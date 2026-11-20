# Problem framing

| Label | Statement |
|---|---|
| Given | Onboarding involves collecting info/docs, review, a proceed decision, and requests for further action. |
| Researched | Traditional life underwriting takes ~3–8 weeks; requests for medical records are the biggest delay (mylifeinsurancecalc.com). |
| Researched | Underwriting referral described as the biggest recoverable leak — a communication failure (kompassify.com insurance onboarding guide). |
| Researched | If automated review flags anything, the file returns to full review and the clock resets (fedlaws.org). |
| Assumption | Fictional insurer SafeLife; term life; illustrative rule thresholds. |
| Hypothesis | Most rework comes from a small set of repeat issues (missing, old, mismatch). |
| Hypothesis | One combined, specific request reduces rounds, time-to-complete-file and drop-off. |

**Candidates considered:** (A) requirements-pending loop — *selected*; (B) mid-application drop-off; (C) black-box wait (partly addressed by tracker).

**Success measures:** rounds per case, % cases needing >1 request, days to complete file, underwriter time per case.

**Validate next:** real case logs for baseline rounds; usability test of request wording.

**Alternatives rejected:** AI auto-decisioning (risk/explainability), upfront checklist only (no quality checks), chatbot (doesn't fix root cause), real OCR/IDV (out of scope).
