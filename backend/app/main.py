"""ClearPath API. Roles are SIMULATED with an 'X-Role' header (applicant / underwriter)."""
import os
from datetime import date
from typing import Literal
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from .rules_engine import load_rules, required_documents
from .checks import check_documents
from .messages import compose_request, maybe_ai_rewrite
from .store import Store

RULES = load_rules()
LABELS = {k: v["label"] for k, v in RULES["documents"].items()}


def today() -> date:  # override for demos/tests via CLEARPATH_TODAY=YYYY-MM-DD
    v = os.getenv("CLEARPATH_TODAY")
    return date.fromisoformat(v) if v else date.today()


class ApplicationIn(BaseModel):
    full_name: str = Field(min_length=2)
    age: int = Field(ge=18, le=65)
    cover_amount: int = Field(gt=0)
    health_answers: dict[str, bool] = {}


class DocumentIn(BaseModel):  # simulated OCR output
    doc_type: str
    name: str
    issued_on: str | None = None
    expires_on: str | None = None
    mentions: list[str] = []


class RequestIn(BaseModel):
    exclude_codes: list[int] = []  # indexes of flagged issues the underwriter dismisses
    extra_issues: list[dict] = []  # underwriter-added issues {code, doc_type, detail}


class DecisionIn(BaseModel):
    decision: Literal["approve", "decline", "refer"]
    note: str = ""


def create_app(store: Store | None = None) -> FastAPI:
    api = FastAPI(title="ClearPath - SafeLife onboarding (prototype)")
    db = store or Store()

    def need_role(role, x_role):
        if x_role != role:
            raise HTTPException(403, f"Only {role} can do this")

    def load(app_id):
        a = db.get(app_id)
        if not a:
            raise HTTPException(404, "Application not found")
        return a

    def recheck(a):
        a["issues"] = check_documents(a, a["requirements"], a["documents"], RULES, today())
        if a["status"] != "DECIDED":
            a["status"] = "UNDER_REVIEW" if not a["issues"] else "REQUIREMENTS_PENDING"

    @api.post("/applications")
    def create(body: ApplicationIn):
        a = {"id": db.new_id(), **body.model_dump(), "documents": {}, "issues": [],
             "rounds": 0, "status": "REQUIREMENTS_PENDING", "decision": None}
        a["requirements"] = required_documents(a, RULES)
        recheck(a)
        db.save(a); db.audit(a["id"], "applicant", "created", [r["doc_type"] for r in a["requirements"]])
        return a

    @api.get("/applications/{app_id}")
    def get(app_id: str):
        a = load(app_id)
        return {**a, "messages": db.outbox_for(app_id)}

    @api.post("/applications/{app_id}/documents")
    def upload(app_id: str, doc: DocumentIn, slot: str, x_role: str = Header("applicant")):
        need_role("applicant", x_role)
        a = load(app_id)
        if a["status"] == "DECIDED":
            raise HTTPException(409, "Application already decided")
        if slot not in {r["doc_type"] for r in a["requirements"]}:
            raise HTTPException(400, f"'{slot}' is not required for this application")
        a["documents"][slot] = doc.model_dump()
        recheck(a)
        db.save(a); db.audit(app_id, "applicant", "uploaded", slot)
        return {"status": a["status"], "issues": a["issues"]}

    @api.get("/underwriter/queue")
    def queue(x_role: str = Header("applicant")):
        need_role("underwriter", x_role)
        return [{"id": a["id"], "name": a["full_name"], "status": a["status"],
                 "open_issues": len(a["issues"]), "rounds": a["rounds"]} for a in db.all()]

    @api.post("/applications/{app_id}/request")
    def send_request(app_id: str, body: RequestIn, x_role: str = Header("applicant")):
        """Underwriter confirms flags -> ONE combined message to applicant."""
        need_role("underwriter", x_role)
        a = load(app_id)
        issues = [i for n, i in enumerate(a["issues"]) if n not in body.exclude_codes] + body.extra_issues
        if not issues:
            raise HTTPException(400, "No issues to request")
        msg = compose_request(issues, LABELS, a["full_name"].split()[0])
        msg = maybe_ai_rewrite(msg, [LABELS[i["doc_type"]] for i in issues])  # off unless enabled
        a["rounds"] += 1; a["status"] = "REQUIREMENTS_PENDING"
        db.save(a); db.send(app_id, msg["body"])
        db.audit(app_id, "underwriter", "request_sent", f"{len(issues)} issues, source={msg['source']}")
        return msg

    @api.post("/applications/{app_id}/decision")
    def decide(app_id: str, body: DecisionIn, x_role: str = Header("applicant")):
        """A HUMAN underwriter makes every decision. Approve blocked while issues are open."""
        need_role("underwriter", x_role)
        a = load(app_id)
        if body.decision == "approve" and a["issues"]:
            raise HTTPException(409, "Cannot approve: open issues remain")
        a["status"], a["decision"] = "DECIDED", body.decision
        db.save(a); db.audit(app_id, "underwriter", f"decision:{body.decision}", body.note)
        return {"status": a["status"], "decision": body.decision}

    @api.get("/applications/{app_id}/audit")
    def audit(app_id: str, x_role: str = Header("applicant")):
        need_role("underwriter", x_role)
        return db.audit_for(app_id)

    return api


app = create_app()
