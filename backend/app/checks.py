"""Instant checks on uploaded documents. Documents are SIMULATED as JSON
(stand-in for OCR output): {doc_type, name, issued_on, expires_on, mentions}."""
from datetime import date
import re

CONDITIONS = ["diabetes", "heart_disease", "hypertension"]


def normalise_name(name: str) -> list[str]:
    return re.sub(r"[^a-z ]", " ", (name or "").lower()).split()


def names_match(a: str, b: str) -> bool:
    """Exact token match. 'Ravi K.' vs 'Ravi Kumar' -> mismatch (flag for human)."""
    return normalise_name(a) == normalise_name(b)


def _d(value):
    return date.fromisoformat(value) if value else None


def check_documents(app: dict, required: list[dict], uploaded: dict, rules: dict,
                    today: date | None = None) -> list[dict]:
    """Return ALL issues at once: [{code, doc_type, detail}]."""
    today = today or date.today()
    issues = []
    for req in required:
        dt = req["doc_type"]
        spec = rules["documents"][dt]
        doc = uploaded.get(dt)
        if not doc:
            issues.append({"code": "MISSING", "doc_type": dt, "detail": f"{req['label']} not uploaded."})
            continue
        if doc.get("doc_type") != dt:
            issues.append({"code": "WRONG_TYPE", "doc_type": dt,
                           "detail": f"Uploaded file looks like '{doc.get('doc_type')}', not {req['label']}."})
            continue
        if not names_match(doc.get("name", ""), app["full_name"]):
            issues.append({"code": "NAME_MISMATCH", "doc_type": dt,
                           "detail": f"Name on document '{doc.get('name')}' does not match '{app['full_name']}'."})
        expires = _d(doc.get("expires_on"))
        if spec.get("must_be_valid") and expires and expires < today:
            issues.append({"code": "EXPIRED", "doc_type": dt, "detail": f"Expired on {expires}."})
        issued = _d(doc.get("issued_on"))
        if spec.get("max_age_days") and issued and (today - issued).days > spec["max_age_days"]:
            issues.append({"code": "TOO_OLD", "doc_type": dt,
                           "detail": f"Dated {issued}; must be within {spec['max_age_days']} days."})
        # Contradiction: document mentions a condition the applicant said NO to
        for cond in doc.get("mentions", []):
            if cond in CONDITIONS and app.get("health_answers", {}).get(cond) is False:
                issues.append({"code": "HEALTH_CONTRADICTION", "doc_type": dt,
                               "detail": f"Document mentions '{cond}' but application answered No."})
    return issues
