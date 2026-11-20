import os
from backend.app.messages import compose_request, maybe_ai_rewrite

LABELS = {"id_proof": "ID proof", "doctor_report": "Doctor's report"}
ISSUES = [{"code": "NAME_MISMATCH", "doc_type": "id_proof", "detail": ""},
          {"code": "TOO_OLD", "doc_type": "doctor_report", "detail": "Dated 2026-02-10; must be within 180 days."}]

def test_one_message_lists_every_issue():
    m = compose_request(ISSUES, LABELS, "Ravi")
    assert m["issue_count"] == 2 and "1." in m["body"] and "2." in m["body"]
    assert "ID proof" in m["body"] and "Doctor's report" in m["body"]

def test_ai_disabled_by_default_uses_template():
    m = compose_request(ISSUES, LABELS)
    assert maybe_ai_rewrite(m, ["ID proof"], rewriter=lambda t: "x")["source"] == "template"

def test_ai_dropping_an_issue_falls_back(monkeypatch):
    monkeypatch.setenv("AI_REWRITE_ENABLED", "true")
    m = compose_request(ISSUES, LABELS)
    bad = lambda t: "1. Please send your ID proof."  # drops doctor's report
    assert maybe_ai_rewrite(m, ["ID proof", "Doctor's report"], bad)["source"] == "template_fallback"

def test_ai_error_falls_back(monkeypatch):
    monkeypatch.setenv("AI_REWRITE_ENABLED", "true")
    def boom(t): raise RuntimeError("service down")
    assert maybe_ai_rewrite(compose_request(ISSUES, LABELS), ["ID proof"], boom)["source"] == "template"

def test_ai_good_rewrite_accepted(monkeypatch):
    monkeypatch.setenv("AI_REWRITE_ENABLED", "true")
    good = lambda t: "Hi! 1. Fix your ID proof name. 2. Send a newer Doctor's report."
    assert maybe_ai_rewrite(compose_request(ISSUES, LABELS), ["ID proof", "Doctor's report"], good)["source"] == "ai_verified"
