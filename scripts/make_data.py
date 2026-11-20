"""Generates SYNTHETIC applicants (no real people). Reference date: 2026-11-20."""
import json
D = lambda t, n, i=None, e=None, m=None: {"doc_type": t, "name": n, "issued_on": i, "expires_on": e, "mentions": m or []}
cases = [
 {"label": "Clean young applicant", "app": {"full_name": "Asha Rao", "age": 29, "cover_amount": 2500000, "health_answers": {"diabetes": False}},
  "docs": {"id_proof": D("id_proof", "Asha Rao", e="2030-01-01"), "address_proof": D("address_proof", "Asha Rao", "2026-10-01")}},
 {"label": "Ravi - 50y, 1.5cr, diabetic, old report + short name", "app": {"full_name": "Ravi Kumar", "age": 50, "cover_amount": 15000000, "health_answers": {"diabetes": True}},
  "docs": {"id_proof": D("id_proof", "Ravi K.", e="2031-05-01"), "address_proof": D("address_proof", "Ravi Kumar", "2026-09-15"),
           "income_proof": D("income_proof", "Ravi Kumar", "2026-04-01"), "medical_exam_report": D("medical_exam_report", "Ravi Kumar", "2026-10-20", m=["diabetes"]),
           "doctor_report": D("doctor_report", "Ravi Kumar", "2026-02-10", m=["diabetes"])}},
 {"label": "Expired ID", "app": {"full_name": "Meera Iyer", "age": 34, "cover_amount": 3000000, "health_answers": {}},
  "docs": {"id_proof": D("id_proof", "Meera Iyer", e="2025-12-31"), "address_proof": D("address_proof", "Meera Iyer", "2026-11-01")}},
 {"label": "Health contradiction", "app": {"full_name": "Karan Shah", "age": 47, "cover_amount": 6000000, "health_answers": {"diabetes": False, "hypertension": False}},
  "docs": {"id_proof": D("id_proof", "Karan Shah", e="2029-01-01"), "address_proof": D("address_proof", "Karan Shah", "2026-10-10"),
           "income_proof": D("income_proof", "Karan Shah", "2026-06-01"), "medical_exam_report": D("medical_exam_report", "Karan Shah", "2026-11-05", m=["hypertension"])}},
 {"label": "Wrong document in slot", "app": {"full_name": "Neha Gupta", "age": 31, "cover_amount": 2000000, "health_answers": {}},
  "docs": {"id_proof": D("id_proof", "Neha Gupta", e="2032-01-01"), "address_proof": D("income_proof", "Neha Gupta", "2026-10-01")}},
 {"label": "Missing everything optional", "app": {"full_name": "Vikram Singh", "age": 55, "cover_amount": 12000000, "health_answers": {"heart_disease": True}},
  "docs": {"id_proof": D("id_proof", "Vikram Singh", e="2030-01-01")}},
 {"label": "Old address proof", "app": {"full_name": "Pooja Nair", "age": 26, "cover_amount": 1500000, "health_answers": {}},
  "docs": {"id_proof": D("id_proof", "Pooja Nair", e="2033-01-01"), "address_proof": D("address_proof", "Pooja Nair", "2026-03-01")}},
 {"label": "Clean high cover", "app": {"full_name": "Arjun Menon", "age": 40, "cover_amount": 8000000, "health_answers": {}},
  "docs": {"id_proof": D("id_proof", "Arjun Menon", e="2031-01-01"), "address_proof": D("address_proof", "Arjun Menon", "2026-11-01"),
           "income_proof": D("income_proof", "Arjun Menon", "2026-08-01")}},
 {"label": "Name with middle name", "app": {"full_name": "Priya Sharma", "age": 38, "cover_amount": 4000000, "health_answers": {}},
  "docs": {"id_proof": D("id_proof", "Priya R. Sharma", e="2030-01-01"), "address_proof": D("address_proof", "Priya Sharma", "2026-10-20")}},
 {"label": "Hypertensive, all good", "app": {"full_name": "Suresh Babu", "age": 46, "cover_amount": 5000000, "health_answers": {"hypertension": True}},
  "docs": {"id_proof": D("id_proof", "Suresh Babu", e="2030-01-01"), "address_proof": D("address_proof", "Suresh Babu", "2026-10-01"),
           "income_proof": D("income_proof", "Suresh Babu", "2026-07-01"), "medical_exam_report": D("medical_exam_report", "Suresh Babu", "2026-10-15", m=["hypertension"]),
           "doctor_report": D("doctor_report", "Suresh Babu", "2026-09-01", m=["hypertension"])}},
]
json.dump(cases, open("data/synthetic_cases.json", "w"), indent=1)
print(len(cases), "cases written")
