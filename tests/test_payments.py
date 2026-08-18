import os
os.environ["DB_FILE"] = "test_payments.db"

from fastapi.testclient import TestClient
from app.main import app, setup

client = TestClient(app)

def reset():
    if os.path.exists("test_payments.db"):
        os.remove("test_payments.db")
    setup()

def test_health():
    assert client.get("/health").json()["status"] == "ok"

def test_add_and_dashboard():
    reset()
    r = client.post("/payments", json={
        "payment_id":"T100",
        "application_id":"A100",
        "amount":1000,
        "status":"paid"
    })
    assert r.status_code == 200
    d = client.get("/dashboard").json()
    assert d["revenue_inr"] == 1000
    assert d["paid_payments"] == 1

def test_failed_payment_creates_alert():
    reset()
    r = client.post("/payments", json={
        "payment_id":"T101",
        "application_id":"A101",
        "amount":500,
        "status":"failed"
    })
    assert r.status_code == 200
    d = client.get("/dashboard").json()
    assert d["failed_payments"] == 1
    assert d["alerts"] == 1

def test_duplicate_payment_is_rejected():
    reset()
    payload = {
        "payment_id":"T102",
        "application_id":"A102",
        "amount":300,
        "status":"paid"
    }
    assert client.post("/payments", json=payload).status_code == 200
    assert client.post("/payments", json=payload).status_code == 409
