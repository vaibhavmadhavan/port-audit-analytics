import sqlite3
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_FILE      = PROJECT_ROOT / "auditpulse.db"
sys.path.insert(0, str(PROJECT_ROOT / "python" / "control_tests"))

import test_duplicate_invoices
import test_rate_breach
import test_preapproval_payment
import test_weekend_payment

def run_all():
    conn      = sqlite3.connect(DB_FILE)
    orders    = pd.read_sql("SELECT * FROM silver_orders", conn)
    contracts = pd.read_sql("SELECT * FROM contracts", conn)
    approvals = pd.read_sql("SELECT * FROM approvals", conn)

    all_exceptions = []

    tests = [
        ("CT001 Duplicate Invoices",   test_duplicate_invoices.run(orders)),
        ("CT002 Rate Breach",          test_rate_breach.run(orders, contracts)),
        ("CT003 Pre-Approval Payment", test_preapproval_payment.run(orders, approvals)),
        ("CT004 Weekend Payment",      test_weekend_payment.run(orders)),
    ]

    for name, df in tests:
        print(f"{name}: {len(df)} exceptions")
        all_exceptions.append(df)

    combined = pd.concat(all_exceptions, ignore_index=True)
    combined['detected_at'] = datetime.now().isoformat()

    combined.to_sql("exceptions", conn, if_exists="replace", index=False)
    combined.to_csv(PROJECT_ROOT / "outputs" / "exceptions.csv", index=False)

    print(f"\nTotal exceptions: {len(combined)}")
    print("Written to DB table 'exceptions' and outputs/exceptions.csv")
    conn.close()

if __name__ == "__main__":
    run_all()