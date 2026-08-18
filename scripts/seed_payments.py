import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.main import add_payment, Payment

sample = [
    ("PAY1001","APP001",1200,"paid"),
    ("PAY1002","APP002",850,"paid"),
    ("PAY1003","APP003",1500,"failed"),
    ("PAY1004","APP004",2100,"paid"),
    ("PAY1005","APP005",600,"pending"),
    ("PAY1006","APP006",950,"refunded"),
    ("PAY1007","APP007",1750,"paid"),
    ("PAY1008","APP008",1250,"paid"),
]
for pid, aid, amount, status in sample:
    try:
        print(add_payment(Payment(payment_id=pid, application_id=aid, amount=amount, status=status)))
    except Exception as e:
        print(pid, "skipped:", e)
print("Seed data loaded.")
