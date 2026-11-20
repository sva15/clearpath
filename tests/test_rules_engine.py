from backend.app.rules_engine import required_documents

def types(app):
    return {r["doc_type"] for r in required_documents(app)}

def test_young_low_cover_needs_only_basics():
    assert types({"age": 29, "cover_amount": 2500000, "health_answers": {}}) == {"id_proof", "address_proof"}

def test_high_cover_needs_income_and_medical():
    t = types({"age": 30, "cover_amount": 15000000, "health_answers": {}})
    assert {"income_proof", "medical_exam_report"} <= t

def test_age_45_boundary_triggers_medical():
    assert "medical_exam_report" in types({"age": 45, "cover_amount": 1000000})
    assert "medical_exam_report" not in types({"age": 44, "cover_amount": 1000000})

def test_declared_condition_needs_doctor_report():
    assert "doctor_report" in types({"age": 30, "cover_amount": 1000000, "health_answers": {"diabetes": True}})

def test_every_requirement_has_reason():
    for r in required_documents({"age": 50, "cover_amount": 20000000, "health_answers": {"diabetes": True}}):
        assert r["reason"]
