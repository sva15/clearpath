"""Builds ONE combined, plain-language request from all issues.
Template-based by default. Optional AI rewording is verified; on failure we fall back."""
import os

TEMPLATES = {
    "MISSING": "Please upload your {label}.",
    "WRONG_TYPE": "The file you sent for {label} seems to be a different document. Please upload your {label}.",
    "NAME_MISMATCH": "The name on your {label} doesn't match your application. Please upload a {label} showing your full name exactly as on the application, or tell us if your name has changed.",
    "EXPIRED": "Your {label} has expired. Please upload a valid one.",
    "TOO_OLD": "Your {label} is too old ({detail}) Please upload a more recent one.",
    "HEALTH_CONTRADICTION": "Your {label} mentions a health condition you answered 'No' to. Please review that answer or add a note for our underwriter.",
}


def compose_request(issues: list[dict], labels: dict, applicant_first_name: str = "there") -> dict:
    lines = []
    for i, iss in enumerate(issues, 1):
        tpl = TEMPLATES[iss["code"]]
        lines.append(f"{i}. " + tpl.format(label=labels[iss["doc_type"]], detail=iss["detail"]))
    body = (f"Hi {applicant_first_name},\n\nTo finish reviewing your SafeLife application we need "
            f"{len(issues)} thing(s). Sorting these out together will avoid further delays:\n\n"
            + "\n".join(lines) + "\n\nYou only need to re-upload the items listed above.")
    return {"body": body, "issue_count": len(issues), "source": "template"}


def verify_rewrite(original: dict, rewritten: str, labels_needed: list[str]) -> bool:
    """Safety check for an AI rewrite: every document label must still appear,
    and numbered item count must be unchanged."""
    text = rewritten.lower()
    has_all = all(l.lower() in text for l in labels_needed)
    count_ok = sum(1 for n in range(1, original["issue_count"] + 1) if f"{n}." in rewritten) == original["issue_count"]
    return has_all and count_ok


def maybe_ai_rewrite(original: dict, labels_needed: list[str], rewriter=None) -> dict:
    """rewriter: callable(text)->text. Only issue text is sent, never documents.
    If AI is disabled, fails, or output fails verification -> template is used."""
    if rewriter is None or os.getenv("AI_REWRITE_ENABLED", "false").lower() != "true":
        return original
    try:
        candidate = rewriter(original["body"])
    except Exception:
        return original
    if verify_rewrite(original, candidate, labels_needed):
        return {**original, "body": candidate, "source": "ai_verified"}
    return {**original, "source": "template_fallback"}
