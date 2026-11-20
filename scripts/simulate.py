"""EXPERIMENT (simulated): rounds of back-and-forth per case.
Baseline assumption: requirements are not known upfront and the reviewer raises
problems one document at a time -> 1 round per document with a problem.
ClearPath: all issues found upfront -> 1 combined round (0 if clean).
Both assume the applicant fixes what is asked correctly (optimistic - a HYPOTHESIS)."""
import json, sys
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app.rules_engine import load_rules, required_documents
from backend.app.checks import check_documents

TODAY = date(2026, 11, 20)
rules = load_rules()
cases = json.load(open(Path(__file__).resolve().parents[1] / "data" / "synthetic_cases.json"))
tb = tc = 0
print(f"{'Case':48} {'Issues':>6} {'Baseline':>8} {'ClearPath':>9}")
for c in cases:
    req = required_documents(c["app"], rules)
    issues = check_documents(c["app"], req, c["docs"], rules, TODAY)
    base = len({i["doc_type"] for i in issues})
    cp = 1 if issues else 0
    tb += base; tc += cp
    print(f"{c['label'][:48]:48} {len(issues):>6} {base:>8} {cp:>9}")
print(f"\nTotal rounds  baseline={tb}  clearpath={tc}  (avg {tb/len(cases):.1f} vs {tc/len(cases):.1f})")
