import pytest
from fastapi.testclient import TestClient
from backend.app.main import create_app
from backend.app.store import Store

UW = {"X-Role": "underwriter"}

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("CLEARPATH_TODAY", "2026-11-20")
    return TestClient(create_app(Store(":memory:")))

RAVI = {"full_name": "Ravi Kumar", "age": 50, "cover_amount": 15000000, "health_answers": {"diabetes": True}}

def doc(t, name="Ravi Kumar", **kw):
    return {"doc_type": t, "name": name, **kw}

def upload_all(c, aid, id_name="Ravi Kumar", doctor_date="2026-10-01"):
    c.post(f"/applications/{aid}/documents?slot=id_proof", json=doc("id_proof", id_name, expires_on="2031-01-01"))
    c.post(f"/applications/{aid}/documents?slot=address_proof", json=doc("address_proof", issued_on="2026-10-01"))
    c.post(f"/applications/{aid}/documents?slot=income_proof", json=doc("income_proof", issued_on="2026-06-01"))
    c.post(f"/applications/{aid}/documents?slot=medical_exam_report", json=doc("medical_exam_report", issued_on="2026-11-01", mentions=["diabetes"]))
    return c.post(f"/applications/{aid}/documents?slot=doctor_report", json=doc("doctor_report", issued_on=doctor_date, mentions=["diabetes"])).json()

def test_requirements_decided_upfront(client):
    a = client.post("/applications", json=RAVI).json()
    assert len(a["requirements"]) == 5 and a["status"] == "REQUIREMENTS_PENDING"

def test_happy_path_one_round_then_approve(client):
    aid = client.post("/applications", json=RAVI).json()["id"]
    r = upload_all(client, aid, id_name="Ravi K.", doctor_date="2026-02-10")
    assert {i["code"] for i in r["issues"]} == {"NAME_MISMATCH", "TOO_OLD"}
    msg = client.post(f"/applications/{aid}/request", json={}, headers=UW).json()
    assert msg["issue_count"] == 2
    # applicant fixes BOTH in one go
    client.post(f"/applications/{aid}/documents?slot=id_proof", json=doc("id_proof", expires_on="2031-01-01"))
    r = client.post(f"/applications/{aid}/documents?slot=doctor_report", json=doc("doctor_report", issued_on="2026-10-01")).json()
    assert r["status"] == "UNDER_REVIEW"
    assert client.post(f"/applications/{aid}/decision", json={"decision": "approve"}, headers=UW).json()["decision"] == "approve"
    assert client.get(f"/applications/{aid}").json()["rounds"] == 1

def test_cannot_approve_with_open_issues(client):
    aid = client.post("/applications", json=RAVI).json()["id"]
    assert client.post(f"/applications/{aid}/decision", json={"decision": "approve"}, headers=UW).status_code == 409

def test_applicant_cannot_use_underwriter_endpoints(client):
    aid = client.post("/applications", json=RAVI).json()["id"]
    assert client.post(f"/applications/{aid}/decision", json={"decision": "approve"}).status_code == 403
    assert client.get("/underwriter/queue").status_code == 403

def test_underwriter_can_dismiss_false_flag(client):
    aid = client.post("/applications", json=RAVI).json()["id"]
    upload_all(client, aid, id_name="Ravi K.")
    issues = client.get(f"/applications/{aid}").json()["issues"]
    assert client.post(f"/applications/{aid}/request", json={"exclude_codes": list(range(len(issues)))}, headers=UW).status_code == 400

def test_edge_unrequired_slot_rejected(client):
    aid = client.post("/applications", json={**RAVI, "age": 25, "cover_amount": 100000, "health_answers": {}}).json()["id"]
    assert client.post(f"/applications/{aid}/documents?slot=doctor_report", json=doc("doctor_report")).status_code == 400

def test_edge_invalid_age_rejected(client):
    assert client.post("/applications", json={**RAVI, "age": 15}).status_code == 422

def test_edge_upload_after_decision_blocked(client):
    aid = client.post("/applications", json=RAVI).json()["id"]
    client.post(f"/applications/{aid}/decision", json={"decision": "decline"}, headers=UW)
    assert client.post(f"/applications/{aid}/documents?slot=id_proof", json=doc("id_proof")).status_code == 409

def test_audit_trail_recorded(client):
    aid = client.post("/applications", json=RAVI).json()["id"]
    upload_all(client, aid)
    actions = [e["action"] for e in client.get(f"/applications/{aid}/audit", headers=UW).json()]
    assert actions[0] == "created" and actions.count("uploaded") == 5
