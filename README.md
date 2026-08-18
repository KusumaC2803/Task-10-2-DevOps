# Task 10 - Monetization Integration & Revenue Dashboard

## What I built

This task adds a small payment monitoring service for PlaceMux.

It stores payment events, calculates revenue from paid payments, tracks failed/refunded/pending payments and creates an alert record when a payment needs attention.

The dashboard is available from the same FastAPI application.

I kept the implementation simple so it is easy to run and verify during the demo.

## Main flow

Payment event -> API -> SQLite -> monitoring summary -> dashboard

A payment with `paid` status is included in revenue.

A `failed` or `refunded` payment creates an alert so it is not silently ignored.

## Run locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/dashboard
- http://127.0.0.1:8000/docs

Load demo data in another terminal:

```bash
python scripts/seed_payments.py
```

## Tests

```bash
pytest -q
```

The tests cover health, revenue calculation, failed payment alerts and duplicate payment protection.

## Load check

With the app running:

```bash
python scripts/load_check.py
```

It sends 50 dashboard requests with 10 workers and prints min/average/p95/max latency.

## Docker

```bash
docker build -t placemux-task10 .
docker run --rm -p 8000:8000 placemux-task10
```

For persistent local data:

```bash
docker run --rm -p 8000:8000 -v "%cd%:/app" placemux-task10
```

## CI

GitHub Actions runs the pytest suite on push and pull request.

No payment gateway secret is stored in this repository.

## Demo steps

1. Start the API.
2. Run the seed script.
3. Open the dashboard.
4. Show the revenue amount and payment counts.
5. Open `/payments` and show the actual stored payment records.
6. Point out that failed/refunded payments create monitoring alerts.
7. Run `pytest -q`.
8. Run the load check and show the p95 result.

## Failure handling

- Duplicate payment IDs return HTTP 409 instead of creating a second record.
- Invalid/zero/negative amounts are rejected.
- Failed and refunded payments are persisted and counted.
- Failed/refunded events create an alert record.
- The service has a `/health` endpoint for a basic deployment check.

## Production note

This demo uses SQLite and a demo payment event API. For real-money mode I would replace SQLite with managed Postgres, verify gateway signatures/webhooks, use idempotency keys from the gateway, put secrets in a secret manager, add authentication/RBAC to the dashboard, and connect alerts to the team's monitoring system.
