from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3
import os
from datetime import datetime

DB_FILE = os.getenv("DB_FILE", "payments.db")
app = FastAPI(title="PlaceMux Payment Monitoring")

def db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def setup():
    conn = db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payment_id TEXT UNIQUE NOT NULL,
            application_id TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL DEFAULT 'INR',
            status TEXT NOT NULL,
            gateway TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payment_id TEXT,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

setup()

class Payment(BaseModel):
    payment_id: str
    application_id: str
    amount: float
    currency: str = "INR"
    status: str
    gateway: str = "demo-gateway"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/payments")
def add_payment(p: Payment):
    if p.amount <= 0:
        raise HTTPException(400, "amount must be positive")
    now = datetime.utcnow().isoformat()
    conn = db()
    try:
        conn.execute(
            """INSERT INTO payments
            (payment_id, application_id, amount, currency, status, gateway, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (p.payment_id, p.application_id, p.amount, p.currency, p.status,
             p.gateway, now, now)
        )
        if p.status.lower() in ("failed", "refunded"):
            conn.execute(
                "INSERT INTO alerts(payment_id, message, created_at) VALUES (?, ?, ?)",
                (p.payment_id, "Payment needs attention: " + p.status, now)
            )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(409, "payment_id already exists")
    conn.close()
    return {"message": "payment recorded", "payment_id": p.payment_id}

@app.get("/payments")
def payments():
    conn = db()
    rows = [dict(x) for x in conn.execute(
        "SELECT * FROM payments ORDER BY id DESC"
    ).fetchall()]
    conn.close()
    return rows

@app.get("/dashboard")
def dashboard():
    conn = db()
    total = conn.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='paid'").fetchone()[0]
    paid_count = conn.execute("SELECT COUNT(*) FROM payments WHERE status='paid'").fetchone()[0]
    failed_count = conn.execute("SELECT COUNT(*) FROM payments WHERE status='failed'").fetchone()[0]
    refunded = conn.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='refunded'").fetchone()[0]
    pending = conn.execute("SELECT COUNT(*) FROM payments WHERE status='pending'").fetchone()[0]
    alerts = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
    conn.close()
    return {
        "revenue_inr": round(total, 2),
        "paid_payments": paid_count,
        "failed_payments": failed_count,
        "refunded_inr": round(refunded, 2),
        "pending_payments": pending,
        "alerts": alerts
    }

@app.get("/", response_class=HTMLResponse)
def home():
    data = dashboard()
    return f"""
    <html>
    <head><title>PlaceMux Revenue Dashboard</title>
    <style>
      body {{ font-family: Arial; margin: 40px; background:#f5f6f8; }}
      h1 {{ margin-bottom: 5px; }}
      .small {{ color:#666; }}
      .grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin-top:25px; }}
      .card {{ background:white; padding:20px; border-radius:10px; box-shadow:0 2px 8px #ddd; }}
      .value {{ font-size:28px; font-weight:bold; margin-top:8px; }}
      .alert {{ margin-top:20px; padding:14px; background:#fff3cd; border-radius:8px; }}
    </style>
    </head>
    <body>
      <h1>PlaceMux Payment Monitoring</h1>
      <div class="small">Simple revenue view for demo and verification</div>
      <div class="grid">
        <div class="card">Revenue<div class="value">₹{data['revenue_inr']:.2f}</div></div>
        <div class="card">Paid payments<div class="value">{data['paid_payments']}</div></div>
        <div class="card">Failed payments<div class="value">{data['failed_payments']}</div></div>
        <div class="card">Refunded<div class="value">₹{data['refunded_inr']:.2f}</div></div>
        <div class="card">Pending<div class="value">{data['pending_payments']}</div></div>
        <div class="card">Alerts<div class="value">{data['alerts']}</div></div>
      </div>
      <div class="alert">
        Payment monitoring is based on persisted payment records. Failed/refunded payments create an alert record.
      </div>
    </body>
    </html>
    """

@app.on_event("startup")
def startup():
    setup()
