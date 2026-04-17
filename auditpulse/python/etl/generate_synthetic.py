import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import date, timedelta
import random

random.seed(42)
np.random.seed(42)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_FILE = PROJECT_ROOT / "auditpulse.db"


def make_vendors():
    categories = ['Stevedoring', 'Fuel', 'Equipment', 'IT', 'Freight Agent', 'Security', 'Maintenance']
    countries  = ['UAE', 'UAE', 'UAE', 'India', 'UK', 'Germany', 'Singapore', 'UAE', 'UAE']
    statuses   = ['Active'] * 40 + ['Dormant'] * 10

    vendors = []
    for i in range(1, 51):
        reg_date = date(2018, 1, 1) + timedelta(days=random.randint(0, 2000))
        vendors.append({
            'vendor_id':          i,
            'vendor_name':        f'Vendor_{i:03d}',
            'vendor_category':    random.choice(categories),
            'country':            random.choice(countries),
            'registration_date':  reg_date.isoformat(),
            'status':             random.choice(statuses),
            'bank_account_hash':  f'HASH_{i:06d}',
        })
    return pd.DataFrame(vendors)


def make_contracts(vendors_df):
    contracts = []
    for i, row in vendors_df.iterrows():
        start = date(2021, 1, 1) + timedelta(days=random.randint(0, 730))
        end   = start + timedelta(days=random.randint(180, 730))
        contracts.append({
            'contract_id':       i + 1,
            'vendor_id':         row['vendor_id'],
            'approved_rate_aed': round(random.uniform(5000, 150000), 2),
            'rate_unit':         random.choice(['per TEU', 'per day', 'lump sum', 'per shipment']),
            'start_date':        start.isoformat(),
            'end_date':          end.isoformat(),
            'max_value_aed':     round(random.uniform(500000, 5000000), 2),
            'approval_level':    random.choice(['Operations', 'Finance', 'Group']),
        })
    return pd.DataFrame(contracts)


def make_terminal_throughput():
    terminals = [
        ('T001', 'Jebel Ali', 'UAE'),
        ('T002', 'Limassol', 'Cyprus'),
        ('T003', 'Southampton', 'UK'),
        ('T004', 'Nhava Sheva', 'India'),
        ('T005', 'Dakar', 'Senegal'),
        ('T006', 'Brisbane', 'Australia'),
    ]
    rows = []
    for tid, tname, region in terminals:
        for year in [2022, 2023, 2024]:
            for month in range(1, 13):
                rows.append({
                    'terminal_id':    tid,
                    'terminal_name':  tname,
                    'region':         region,
                    'year':           year,
                    'month':          month,
                    'teu_actual':     random.randint(15000, 80000),
                    'vessel_calls':   random.randint(30, 120),
                })
    return pd.DataFrame(rows)


def make_approvals(n=2000):
    levels = ['Operations', 'Finance', 'Group']
    rows = []
    for i in range(1, n + 1):
        ap_date = date(2022, 1, 1) + timedelta(days=random.randint(0, 900))
        rows.append({
            'approval_id':     i,
            'transaction_ref': f'TXN_{i:06d}',
            'approver_id':     random.randint(1, 30),
            'approval_level':  random.choice(levels),
            'approved_amount': round(random.uniform(1000, 500000), 2),
            'approval_date':   ap_date.isoformat(),
            'outcome':         random.choice(['Approved'] * 9 + ['Rejected']),
        })
    return pd.DataFrame(rows)


def main():
    conn = sqlite3.connect(DB_FILE)

    vendors_df = make_vendors()
    vendors_df.to_sql("vendors", conn, if_exists="replace", index=False)
    print(f"vendors: {len(vendors_df)} rows")

    contracts_df = make_contracts(vendors_df)
    contracts_df.to_sql("contracts", conn, if_exists="replace", index=False)
    print(f"contracts: {len(contracts_df)} rows")

    throughput_df = make_terminal_throughput()
    throughput_df.to_sql("terminal_throughput", conn, if_exists="replace", index=False)
    print(f"terminal_throughput: {len(throughput_df)} rows")

    approvals_df = make_approvals()
    approvals_df.to_sql("approvals", conn, if_exists="replace", index=False)
    print(f"approvals: {len(approvals_df)} rows")

    # Confirm all tables
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print("\nAll tables in DB:", cur.fetchall())
    conn.close()

if __name__ == "__main__":
    main()