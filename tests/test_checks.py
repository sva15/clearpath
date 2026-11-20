from datetime import date
from backend.app.rules_engine import load_rules, required_documents
from backend.app.checks import check_documents, names_match

R = load_rules(); TODAY = date(2026, 11, 20)
APP = {"full_name": "Ravi Kumar", "age": 30, "cover_amount": 1000000, "health_answers": {"diabetes": False}}
REQ = required_documents(APP, R)
OK = {"id_proof": {"doc_type": "id_proof", "name": "Ravi Kumar", "expires_on": "2030-01-01"},
      "address_proof": {"doc_type": "address_proof", "name": "Ravi Kumar", "issued_on": "2026-10-01"}}

def codes(docs, app=APP):
    return [i["code"] for i in check_documents(app, REQ, docs, R, TODAY)]

def test_clean_file_has_no_issues():
    assert codes(OK) == []

def test_all_issues_returned_together():
    docs = {"id_proof": {**OK["id_proof"], "name": "Ravi K.", "expires_on": "2025-01-01"}}
    assert set(codes(docs)) == {"NAME_MISMATCH", "EXPIRED", "MISSING"}

def test_too_old_address_proof():
    assert codes({**OK, "address_proof": {**OK["address_proof"], "issued_on": "2026-01-01"}}) == ["TOO_OLD"]

def test_wrong_type_in_slot():
    assert codes({**OK, "address_proof": {**OK["address_proof"], "doc_type": "income_proof"}}) == ["WRONG_TYPE"]

def test_health_contradiction_detected():
    docs = {**OK, "address_proof": {**OK["address_proof"], "mentions": ["diabetes"]}}
    assert "HEALTH_CONTRADICTION" in codes(docs)

def test_name_normalisation():
    assert names_match("RAVI  kumar", "Ravi Kumar")
    assert not names_match("Ravi K.", "Ravi Kumar")

def test_edge_middle_initial_is_flagged_for_human():
    # Known limitation: conservative match -> human underwriter decides
    assert not names_match("Priya R. Sharma", "Priya Sharma")

def test_edge_document_expiring_exactly_today_is_still_valid():
    assert codes({**OK, "id_proof": {**OK["id_proof"], "expires_on": "2026-11-20"}}) == []
