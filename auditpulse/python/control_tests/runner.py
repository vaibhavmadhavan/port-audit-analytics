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
import test_new_vendor_risk
import test_contract_expiry
import test_teu_volume_mismatch
import test_split_billing

def run_all():
    conn       = sqlite3.connect(DB_FILE)
    orders     = pd.read_sql("SELECT * FROM silver_orders",      conn)
    contracts  = pd.read_sql("SELECT * FROM contracts",          conn)
    approvals  = pd.read_sql("SELECT * FROM approvals",          conn)
    vendors    = pd.read_sql("SELECT * FROM vendors",            conn)
    throughput = pd.read_sql("SELECT * FROM terminal_throughput",conn)

    tests = [
        ("CT001 Duplicate Invoices",     test_duplicate_invoices.run(orders)),
        ("CT002 Rate Breach",            test_rate_breach.run(orders, contracts)),
        ("CT003 Pre-Approval Payment",   test_preapproval_payment.run(orders, approvals)),
        ("CT004 Weekend Payment",        test_weekend_payment.run(orders)),
        ("CT005 New Vendor Risk",        test_new_vendor_risk.run(orders, vendors)),
        ("CT006 Contract Expiry Bypass", test_contract_expiry.run(orders, contracts)),
        ("CT007 TEU Volume Mismatch",    test_teu_volume_mismatch.run(orders, throughput)),
        ("CT008 Split Billing",          test_split_billing.run(orders)),
    ]

    all_exceptions = []
    print("\n=== AUDIT CONTROL TEST RESULTS ===")
    for name, df in tests:
        # normalise 'week' period column to string so SQLite can store it
        if 'week' in df.columns:
            df['week'] = df['week'].astype(str)
        print(f"{name}: {len(df)} exceptions")
        all_exceptions.append(df)

    combined = pd.concat(all_exceptions, ignore_index=True)
    combined['detected_at'] = datetime.now().isoformat()

    combined.to_sql("exceptions", conn, if_exists="replace", index=False)
    combined.to_csv(PROJECT_ROOT / "outputs" / "exceptions.csv", index=False)

    print(f"\nTotal exceptions written: {len(combined)}")
    print(f"HIGH:   {(combined['severity']=='HIGH').sum()}")
    print(f"MEDIUM: {(combined['severity']=='MEDIUM').sum()}")
    print(f"LOW:    {(combined['severity']=='LOW').sum()}")
    print("\nWritten to DB table 'exceptions' and outputs/exceptions.csv")
    conn.close()

if __name__ == "__main__":
    run_all()