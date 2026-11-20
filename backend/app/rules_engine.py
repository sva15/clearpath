"""Works out which documents an applicant must provide, and why."""
from pathlib import Path
import yaml

RULES_PATH = Path(__file__).resolve().parents[2] / "rules" / "term_life.yaml"


def load_rules(path=RULES_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _condition_met(cond: dict, app: dict) -> bool:
    if "age_gte" in cond:
        return app["age"] >= cond["age_gte"]
    if "cover_amount_gte" in cond:
        return app["cover_amount"] >= cond["cover_amount_gte"]
    if "any_health_yes" in cond:
        answers = app.get("health_answers", {})
        return any(answers.get(c) is True for c in cond["any_health_yes"])
    raise ValueError(f"Unknown condition: {cond}")


def required_documents(app: dict, rules: dict | None = None) -> list[dict]:
    """Return [{doc_type, label, reason}] - every requirement, decided UPFRONT."""
    rules = rules or load_rules()
    docs = rules["documents"]
    result = {d: "Required for every applicant." for d in rules["always"]}
    for rule in rules["rules"]:
        if "when" in rule:
            met = _condition_met(rule["when"], app)
        else:
            met = any(_condition_met(c, app) for c in rule["when_any"])
        if met:
            for d in rule["require"]:
                result.setdefault(d, rule["reason"])
    return [{"doc_type": d, "label": docs[d]["label"], "reason": r} for d, r in result.items()]
