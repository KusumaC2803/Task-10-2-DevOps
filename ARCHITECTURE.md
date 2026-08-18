# Simple Architecture

```text
Payment event
     |
     v
FastAPI /payments
     |
     v
SQLite payment records
     |
     +----> failed/refunded -> alert record
     |
     v
/dashboard
     |
     v
Revenue + payment health metrics
```

The project is intentionally small and readable for the student demo.
