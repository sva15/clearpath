"""Tiny SQLite store. Each application is saved as a JSON blob + an audit table."""
import json, sqlite3, os, uuid
from datetime import datetime, timezone

DB_PATH = os.getenv("CLEARPATH_DB", "clearpath.db")


class Store:
    def __init__(self, path: str = DB_PATH):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.execute("CREATE TABLE IF NOT EXISTS applications (id TEXT PRIMARY KEY, data TEXT)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS audit (app_id TEXT, at TEXT, actor TEXT, action TEXT, detail TEXT)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS outbox (app_id TEXT, at TEXT, body TEXT)")
        self.conn.commit()

    def new_id(self) -> str:
        return "APP-" + uuid.uuid4().hex[:6].upper()

    def save(self, app: dict):
        self.conn.execute("INSERT OR REPLACE INTO applications VALUES (?, ?)", (app["id"], json.dumps(app)))
        self.conn.commit()

    def get(self, app_id: str) -> dict | None:
        row = self.conn.execute("SELECT data FROM applications WHERE id=?", (app_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def all(self) -> list[dict]:
        return [json.loads(r[0]) for r in self.conn.execute("SELECT data FROM applications")]

    def audit(self, app_id, actor, action, detail=""):
        self.conn.execute("INSERT INTO audit VALUES (?,?,?,?,?)",
                          (app_id, datetime.now(timezone.utc).isoformat(), actor, action, str(detail)))
        self.conn.commit()

    def audit_for(self, app_id):
        rows = self.conn.execute("SELECT at, actor, action, detail FROM audit WHERE app_id=? ORDER BY at", (app_id,))
        return [dict(zip(["at", "actor", "action", "detail"], r)) for r in rows]

    def send(self, app_id, body):  # SIMULATED email
        self.conn.execute("INSERT INTO outbox VALUES (?,?,?)",
                          (app_id, datetime.now(timezone.utc).isoformat(), body))
        self.conn.commit()

    def outbox_for(self, app_id):
        rows = self.conn.execute("SELECT at, body FROM outbox WHERE app_id=? ORDER BY at", (app_id,))
        return [{"at": a, "body": b} for a, b in rows]
