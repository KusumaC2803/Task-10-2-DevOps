# Task 10 Runbook

## Before demo

- Confirm Docker/Python is available.
- Install requirements.
- Run tests.
- Start the API.
- Seed the sample payment records.

## Health check

```bash
curl http://127.0.0.1:8000/health
```

Expected:

```json
{"status":"ok"}
```

## Revenue verification

```bash
curl http://127.0.0.1:8000/dashboard
```

Revenue is calculated only from records with `status = paid`.

## Failure verification

Create a failed payment:

```bash
curl -X POST http://127.0.0.1:8000/payments ^
  -H "Content-Type: application/json" ^
  -d "{\"payment_id\":\"FAIL001\",\"application_id\":\"APPFAIL\",\"amount\":700,\"status\":\"failed\"}"
```

Then check `/dashboard`. Failed payment count and alerts should increase.

## Rollback

If a new image fails its health check, stop the new container and run the last known working image.

```bash
docker ps
docker stop <container_id>
docker run --rm -p 8000:8000 placemux-task10:<known-good-tag>
```

## Real-money checklist

Before switching from demo/test mode:

- Verify gateway webhook signature.
- Use idempotency protection.
- Store secrets outside git.
- Use managed Postgres.
- Add alert routing.
- Test refund and partial-failure cases.
- Reconcile internal records against gateway settlement reports.

## What can go wrong

### Payment succeeded at gateway but app did not update

Keep the payment event retryable and reconcile against gateway records. Do not assume a missing local record means the gateway failed.

### Same event arrives twice

Use the gateway payment/event ID as an idempotency key. This demo protects `payment_id` with a unique database constraint.

### Payment failed halfway

Persist the failed state and create an alert. The application record should not silently look paid.

### Dashboard numbers do not match gateway

Run a reconciliation job using gateway transaction IDs and settlement data before declaring revenue correct.
