"""ClearPath demo UI. Run the API first: uvicorn backend.app.main:app --reload"""
import json, os
from pathlib import Path
import requests
import streamlit as st

API = os.getenv("CLEARPATH_API", "http://localhost:8000")
CASES = json.load(open(Path(__file__).resolve().parents[1] / "data" / "synthetic_cases.json"))
STAGES = ["REQUIREMENTS_PENDING", "UNDER_REVIEW", "DECIDED"]

st.set_page_config(page_title="ClearPath - SafeLife", layout="wide")
st.title("ClearPath · SafeLife term-life onboarding (prototype)")
st.caption("Fictional insurer · synthetic data · documents and email are simulated")
role = st.sidebar.radio("Simulated login", ["Applicant", "Underwriter"])
H = {"X-Role": role.lower()}

def show_app(a):
    st.progress((STAGES.index(a["status"]) + 1) / len(STAGES), text=f"Status: {a['status']}  ·  rounds: {a['rounds']}")
    st.subheader("What we need and why")
    st.table([{"Document": r["label"], "Why": r["reason"],
               "Uploaded": "Yes" if r["doc_type"] in a["documents"] else "No"} for r in a["requirements"]])

if role == "Applicant":
    tab1, tab2 = st.tabs(["New application", "My application"])
    with tab1:
        pick = st.selectbox("Quick-fill a synthetic case (demo)", ["-"] + [c["label"] for c in CASES])
        case = next((c for c in CASES if c["label"] == pick), None)
        if case and st.button("Submit this case with its documents"):
            a = requests.post(f"{API}/applications", json=case["app"]).json()
            for slot, d in case["docs"].items():
                requests.post(f"{API}/applications/{a['id']}/documents", params={"slot": slot}, json=d, headers=H)
            st.session_state["app_id"] = a["id"]
            st.success(f"Submitted {a['id']}. Open the 'My application' tab.")
        with st.form("new"):
            name = st.text_input("Full name"); age = st.number_input("Age", 18, 65, 30)
            cover = st.number_input("Cover amount (Rs)", 100000, 50000000, 2500000, step=500000)
            dia = st.checkbox("Diabetes?"); heart = st.checkbox("Heart disease?"); hyp = st.checkbox("Hypertension?")
            if st.form_submit_button("Start application"):
                r = requests.post(f"{API}/applications", json={"full_name": name, "age": int(age), "cover_amount": int(cover),
                                  "health_answers": {"diabetes": dia, "heart_disease": heart, "hypertension": hyp}})
                if r.ok: st.session_state["app_id"] = r.json()["id"]; st.success(f"Created {r.json()['id']}")
                else: st.error(r.json()["detail"])
    with tab2:
        aid = st.text_input("Application ID", st.session_state.get("app_id", ""))
        if aid:
            a = requests.get(f"{API}/applications/{aid}").json()
            if "id" not in a: st.error("Not found"); st.stop()
            show_app(a)
            for m in a["messages"][::-1]:
                st.info(m["body"])
            if a["status"] != "DECIDED":
                st.subheader("Upload / re-upload (simulated document)")
                with st.form("up"):
                    slot = st.selectbox("Requirement", [r["doc_type"] for r in a["requirements"]])
                    dname = st.text_input("Name on document", a["full_name"])
                    issued = st.text_input("Issued on (YYYY-MM-DD)", "")
                    expires = st.text_input("Expires on (YYYY-MM-DD)", "")
                    if st.form_submit_button("Upload"):
                        r = requests.post(f"{API}/applications/{aid}/documents", params={"slot": slot}, headers=H,
                                          json={"doc_type": slot, "name": dname, "issued_on": issued or None, "expires_on": expires or None})
                        st.write(r.json()); st.rerun()
            else:
                st.success(f"Decision: {a['decision']}")
else:
    q = requests.get(f"{API}/underwriter/queue", headers=H).json()
    st.subheader("Case queue"); st.dataframe(q, use_container_width=True)
    if q:
        aid = st.selectbox("Open case", [c["id"] for c in q])
        a = requests.get(f"{API}/applications/{aid}").json()
        st.markdown(f"**{a['full_name']}** · age {a['age']} · cover Rs {a['cover_amount']:,} · health {a['health_answers']}")
        show_app(a)
        st.subheader("Auto-flagged issues (confirm or dismiss)")
        dismiss = [n for n, i in enumerate(a["issues"])
                   if not st.checkbox(f"{i['code']} - {i['detail']}", value=True, key=f"{aid}{n}")]
        c1, c2 = st.columns(2)
        if c1.button("Send ONE combined request", disabled=not a["issues"] or a["status"] == "DECIDED"):
            r = requests.post(f"{API}/applications/{aid}/request", json={"exclude_codes": dismiss}, headers=H)
            st.info(r.json().get("body", r.json())); 
        with c2:
            dec = st.selectbox("Decision (human)", ["approve", "decline", "refer"])
            note = st.text_input("Note")
            if st.button("Record decision", disabled=a["status"] == "DECIDED"):
                r = requests.post(f"{API}/applications/{aid}/decision", json={"decision": dec, "note": note}, headers=H)
                st.write(r.json())
        with st.expander("Audit trail"):
            st.table(requests.get(f"{API}/applications/{aid}/audit", headers=H).json())
