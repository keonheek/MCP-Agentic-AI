"""
Database layer for ERP Demo — SQLite CRUD + dashboard queries.
All monetary values in KRW (INTEGER). Status fields enforced in Python.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path

# Store DB in temp dir to avoid Korean path issues on Windows
import tempfile as _tempfile
_TEMP_DB_DIR = Path(_tempfile.gettempdir()) / "erp_demo"
_TEMP_DB_DIR.mkdir(exist_ok=True)
DB_PATH = _TEMP_DB_DIR / "erp_demo.db"
# Schema file stays in project dir (read-only, works fine)
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

CLIENT_STATUSES = ("lead", "contacted", "quoted", "converted", "retainer", "churned")
QUOTE_STATUSES = ("draft", "sent", "accepted", "rejected", "expired")
INVOICE_STATUSES = ("unpaid", "paid", "overdue", "cancelled")
INTERACTION_TYPES = ("call", "kakao", "email", "meeting", "note")
MESSAGE_TYPES = ("followup", "speed_to_lead", "reactivation")
SOURCES = ("soomgo", "kmong", "kakao", "referral", "naver", "other")


@contextmanager
def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


# ─── Clients ───────────────────────────────────────────────

def list_clients(status: str | None = None, search: str | None = None) -> list[dict]:
    q = "SELECT * FROM clients WHERE 1=1"
    params = []
    if status:
        q += " AND status = ?"
        params.append(status)
    if search:
        q += " AND (name LIKE ? OR business_name LIKE ? OR kakao_id LIKE ?)"
        params.extend([f"%{search}%"] * 3)
    q += " ORDER BY updated_at DESC"
    with get_db() as conn:
        return [dict(r) for r in conn.execute(q, params).fetchall()]


def get_client(client_id: int) -> dict | None:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
        return dict(row) if row else None


def create_client(**kwargs) -> int:
    cols = ["name", "business_name", "phone", "email", "kakao_id",
            "website", "status", "source", "geo_score", "notes"]
    data = {k: kwargs.get(k) for k in cols if kwargs.get(k) is not None}
    if not data.get("name") or not data.get("business_name"):
        raise ValueError("name and business_name are required")
    keys = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    with get_db() as conn:
        cur = conn.execute(
            f"INSERT INTO clients ({keys}) VALUES ({placeholders})",
            list(data.values()),
        )
        return cur.lastrowid


def update_client(client_id: int, **kwargs) -> None:
    allowed = ["name", "business_name", "phone", "email", "kakao_id",
               "website", "status", "source", "geo_score", "notes"]
    data = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not data:
        return
    data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sets = ", ".join(f"{k} = ?" for k in data)
    with get_db() as conn:
        conn.execute(f"UPDATE clients SET {sets} WHERE id = ?",
                     list(data.values()) + [client_id])


def delete_client(client_id: int) -> None:
    with get_db() as conn:
        conn.execute("DELETE FROM clients WHERE id = ?", (client_id,))


# ─── Interactions ──────────────────────────────────────────

def list_interactions(client_id: int) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM interactions WHERE client_id = ? ORDER BY created_at DESC",
            (client_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def add_interaction(client_id: int, type: str, content: str) -> int:
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO interactions (client_id, type, content) VALUES (?, ?, ?)",
            (client_id, type, content),
        )
        conn.execute(
            "UPDATE clients SET updated_at = ? WHERE id = ?",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), client_id),
        )
        return cur.lastrowid


# ─── Quotes ────────────────────────────────────────────────

def next_quote_number() -> str:
    year = datetime.now().year
    with get_db() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM quotes WHERE quote_number LIKE ?",
            (f"GEO-{year}-%",),
        ).fetchone()
        n = (row["cnt"] if row else 0) + 1
        return f"GEO-{year}-{n:03d}"


def list_quotes(status: str | None = None, client_id: int | None = None) -> list[dict]:
    q = """SELECT q.*, c.business_name,
           COALESCE((SELECT SUM(quantity * unit_price) FROM quote_items WHERE quote_id = q.id), 0) as total
           FROM quotes q JOIN clients c ON q.client_id = c.id WHERE 1=1"""
    params = []
    if status:
        q += " AND q.status = ?"
        params.append(status)
    if client_id:
        q += " AND q.client_id = ?"
        params.append(client_id)
    q += " ORDER BY q.created_at DESC"
    with get_db() as conn:
        return [dict(r) for r in conn.execute(q, params).fetchall()]


def get_quote(quote_id: int) -> dict | None:
    with get_db() as conn:
        row = conn.execute(
            """SELECT q.*, c.name as client_name, c.business_name, c.phone, c.email, c.kakao_id
               FROM quotes q JOIN clients c ON q.client_id = c.id WHERE q.id = ?""",
            (quote_id,),
        ).fetchone()
        if not row:
            return None
        q = dict(row)
        q["items"] = [dict(r) for r in conn.execute(
            "SELECT * FROM quote_items WHERE quote_id = ? ORDER BY sort_order",
            (quote_id,),
        ).fetchall()]
        q["total"] = sum(i["quantity"] * i["unit_price"] for i in q["items"])
        return q


def create_quote(client_id: int, title: str, items: list[dict],
                 valid_until: str | None = None, notes: str | None = None) -> int:
    qnum = next_quote_number()
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO quotes (client_id, quote_number, title, valid_until, notes) VALUES (?, ?, ?, ?, ?)",
            (client_id, qnum, title, valid_until, notes),
        )
        qid = cur.lastrowid
        for i, item in enumerate(items):
            conn.execute(
                "INSERT INTO quote_items (quote_id, description, quantity, unit_price, sort_order) VALUES (?, ?, ?, ?, ?)",
                (qid, item["description"], item.get("quantity", 1), item["unit_price"], i),
            )
        return qid


def update_quote_status(quote_id: int, status: str) -> None:
    with get_db() as conn:
        conn.execute(
            "UPDATE quotes SET status = ?, updated_at = ? WHERE id = ?",
            (status, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), quote_id),
        )


# ─── Invoices ──────────────────────────────────────────────

def next_invoice_number() -> str:
    year = datetime.now().year
    with get_db() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM invoices WHERE invoice_number LIKE ?",
            (f"INV-{year}-%",),
        ).fetchone()
        n = (row["cnt"] if row else 0) + 1
        return f"INV-{year}-{n:03d}"


def list_invoices(status: str | None = None, client_id: int | None = None) -> list[dict]:
    q = """SELECT i.*, c.business_name, q.quote_number
           FROM invoices i
           JOIN clients c ON i.client_id = c.id
           LEFT JOIN quotes q ON i.quote_id = q.id
           WHERE 1=1"""
    params = []
    if status:
        q += " AND i.status = ?"
        params.append(status)
    if client_id:
        q += " AND i.client_id = ?"
        params.append(client_id)
    q += " ORDER BY i.issued_at DESC"
    with get_db() as conn:
        return [dict(r) for r in conn.execute(q, params).fetchall()]


def create_invoice_from_quote(quote_id: int, due_date: str | None = None) -> int:
    q = get_quote(quote_id)
    if not q:
        raise ValueError(f"Quote {quote_id} not found")
    if not due_date:
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    inum = next_invoice_number()
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO invoices (quote_id, client_id, invoice_number, total_amount, due_date) VALUES (?, ?, ?, ?, ?)",
            (quote_id, q["client_id"], inum, q["total"], due_date),
        )
        return cur.lastrowid


def create_invoice_manual(client_id: int, total_amount: int, due_date: str | None = None) -> int:
    if not due_date:
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    inum = next_invoice_number()
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO invoices (client_id, invoice_number, total_amount, due_date) VALUES (?, ?, ?, ?)",
            (client_id, inum, total_amount, due_date),
        )
        return cur.lastrowid


def update_invoice_status(invoice_id: int, status: str) -> None:
    paid_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if status == "paid" else None
    with get_db() as conn:
        conn.execute(
            "UPDATE invoices SET status = ?, paid_at = ? WHERE id = ?",
            (status, paid_at, invoice_id),
        )


def get_invoice(invoice_id: int) -> dict | None:
    with get_db() as conn:
        row = conn.execute(
            """SELECT i.*, c.name as client_name, c.business_name, c.phone, c.email, c.kakao_id
               FROM invoices i JOIN clients c ON i.client_id = c.id WHERE i.id = ?""",
            (invoice_id,),
        ).fetchone()
        if not row:
            return None
        inv = dict(row)
        if inv.get("quote_id"):
            q = get_quote(inv["quote_id"])
            inv["items"] = q["items"] if q else []
        else:
            inv["items"] = []
        return inv


# ─── Message Queue ─────────────────────────────────────────

def queue_message(client_id: int, type: str, message: str, channel: str = "kakao") -> int:
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO message_queue (client_id, type, channel, message) VALUES (?, ?, ?, ?)",
            (client_id, type, channel, message),
        )
        return cur.lastrowid


def list_messages(status: str | None = None, type: str | None = None) -> list[dict]:
    q = """SELECT m.*, c.name as client_name, c.business_name
           FROM message_queue m JOIN clients c ON m.client_id = c.id WHERE 1=1"""
    params = []
    if status:
        q += " AND m.status = ?"
        params.append(status)
    if type:
        q += " AND m.type = ?"
        params.append(type)
    q += " ORDER BY m.created_at DESC"
    with get_db() as conn:
        return [dict(r) for r in conn.execute(q, params).fetchall()]


def update_message_status(message_id: int, status: str) -> None:
    with get_db() as conn:
        conn.execute("UPDATE message_queue SET status = ? WHERE id = ?", (status, message_id))


# ─── Dashboard Queries ─────────────────────────────────────

def pipeline_counts() -> dict:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT status, COUNT(*) as cnt FROM clients GROUP BY status"
        ).fetchall()
        return {r["status"]: r["cnt"] for r in rows}


def total_clients() -> int:
    with get_db() as conn:
        row = conn.execute("SELECT COUNT(*) as cnt FROM clients").fetchone()
        return row["cnt"]


def conversion_rate() -> float:
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) as cnt FROM clients").fetchone()["cnt"]
        if total == 0:
            return 0.0
        converted = conn.execute(
            "SELECT COUNT(*) as cnt FROM clients WHERE status IN ('converted', 'retainer')"
        ).fetchone()["cnt"]
        return round(converted / total * 100, 1)


def open_quotes_value() -> int:
    with get_db() as conn:
        row = conn.execute(
            """SELECT COALESCE(SUM(qi.quantity * qi.unit_price), 0) as total
               FROM quotes q JOIN quote_items qi ON q.id = qi.quote_id
               WHERE q.status IN ('draft', 'sent')"""
        ).fetchone()
        return row["total"]


def monthly_revenue(year: int | None = None, month: int | None = None) -> int:
    now = datetime.now()
    y = year or now.year
    m = month or now.month
    start = f"{y}-{m:02d}-01"
    if m == 12:
        end = f"{y + 1}-01-01"
    else:
        end = f"{y}-{m + 1:02d}-01"
    with get_db() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(total_amount), 0) as total FROM invoices WHERE status = 'paid' AND paid_at >= ? AND paid_at < ?",
            (start, end),
        ).fetchone()
        return row["total"]


def recent_activity(limit: int = 10) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            """SELECT i.*, c.name as client_name, c.business_name
               FROM interactions i JOIN clients c ON i.client_id = c.id
               ORDER BY i.created_at DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def expiring_quotes(days: int = 7) -> list[dict]:
    cutoff = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    with get_db() as conn:
        rows = conn.execute(
            """SELECT q.*, c.business_name,
               COALESCE((SELECT SUM(quantity * unit_price) FROM quote_items WHERE quote_id = q.id), 0) as total
               FROM quotes q JOIN clients c ON q.client_id = c.id
               WHERE q.status IN ('draft', 'sent') AND q.valid_until IS NOT NULL
               AND q.valid_until >= ? AND q.valid_until <= ?
               ORDER BY q.valid_until""",
            (today, cutoff),
        ).fetchall()
        return [dict(r) for r in rows]


def overdue_invoices() -> list[dict]:
    today = datetime.now().strftime("%Y-%m-%d")
    with get_db() as conn:
        rows = conn.execute(
            """SELECT i.*, c.business_name
               FROM invoices i JOIN clients c ON i.client_id = c.id
               WHERE i.status = 'unpaid' AND i.due_date < ?
               ORDER BY i.due_date""",
            (today,),
        ).fetchall()
        return [dict(r) for r in rows]


def cold_leads(days: int = 14) -> list[dict]:
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    with get_db() as conn:
        rows = conn.execute(
            """SELECT c.* FROM clients c
               WHERE c.status NOT IN ('converted', 'retainer', 'churned')
               AND c.updated_at < ?
               ORDER BY c.updated_at""",
            (cutoff,),
        ).fetchall()
        return [dict(r) for r in rows]


def message_stats() -> dict:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT status, COUNT(*) as cnt FROM message_queue GROUP BY status"
        ).fetchall()
        return {r["status"]: r["cnt"] for r in rows}
