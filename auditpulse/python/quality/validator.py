import sqlite3
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_FILE      = PROJECT_ROOT / "auditpulse.db"

def run_checks():
    conn    = sqlite3.connect(DB_FILE)
    results = []

    orders    = pd.read_sql("SELECT * FROM silver_orders", conn)
    vendors   = pd.read_sql("SELECT * FROM vendors", conn)
    contracts = pd.read_sql("SELECT * FROM contracts", conn)
    approvals = pd.read_sql("SELECT * FROM approvals", conn)

    # 1. COMPLETENESS
    checks = [
        ('silver_orders', orders,    ['order_id','order_date','sales_amount','order_status']),
        ('vendors',       vendors,   ['vendor_id','vendor_name','vendor_category','status']),
        ('contracts',     contracts, ['contract_id','vendor_id','approved_rate_aed','end_date']),
        ('approvals',     approvals, ['approval_id','approved_amount','approval_date','outcome']),
    ]
    for tname, df, fields in checks:
        for field in fields:
            if field not in df.columns: continue
            n    = df[field].isna().sum()
            rate = round(n / len(df) * 100, 2)
            results.append({'check_category':'Completeness','check_name':f'Null: {tname}.{field}',
                'table':tname,'field':field,'issue_count':int(n),'issue_rate_pct':rate,
                'severity':'HIGH' if rate>5 else('MEDIUM' if rate>1 else 'LOW'),
                'note':f'{n} nulls ({rate}%)'})

    # 2. UNIQUENESS
    for tname, df, col in [('silver_orders',orders,'order_id'),('vendors',vendors,'vendor_id')]:
        n    = df.duplicated(subset=[col]).sum()
        rate = round(n/len(df)*100,2)
        results.append({'check_category':'Uniqueness','check_name':f'Duplicate {col} in {tname}',
            'table':tname,'field':col,'issue_count':int(n),'issue_rate_pct':rate,
            'severity':'HIGH' if n>0 else 'LOW','note':f'{n} duplicate {col}s'})

    # 3. CONSISTENCY
    orphans = len(set(contracts['vendor_id']) - set(vendors['vendor_id']))
    results.append({'check_category':'Consistency','check_name':'Contracts with unknown vendor_id',
        'table':'contracts','field':'vendor_id','issue_count':orphans,
        'issue_rate_pct':round(orphans/len(contracts)*100,2),
        'severity':'HIGH' if orphans>0 else 'LOW',
        'note':f'{orphans} contracts reference missing vendor IDs'})

    # 4. ACCURACY
    neg = (orders['sales_amount'] < 0).sum()
    results.append({'check_category':'Accuracy','check_name':'Negative sales_amount',
        'table':'silver_orders','field':'sales_amount','issue_count':int(neg),
        'issue_rate_pct':round(neg/len(orders)*100,2),
        'severity':'HIGH' if neg>0 else 'LOW','note':f'{neg} negative sales amounts'})

    neg_ap = (approvals['approved_amount'] <= 0).sum()
    results.append({'check_category':'Accuracy','check_name':'Zero/negative approved_amount',
        'table':'approvals','field':'approved_amount','issue_count':int(neg_ap),
        'issue_rate_pct':round(neg_ap/len(approvals)*100,2),
        'severity':'HIGH' if neg_ap>0 else 'LOW','note':f'{neg_ap} zero/negative approvals'})

    # 5. TIMELINESS
    orders['order_date'] = pd.to_datetime(orders['order_date'], errors='coerce')
    orders['ship_date']  = pd.to_datetime(orders['ship_date'],  errors='coerce')
    late = (orders['ship_date'] < orders['order_date']).sum()
    results.append({'check_category':'Timeliness','check_name':'Ship date before order date',
        'table':'silver_orders','field':'ship_date','issue_count':int(late),
        'issue_rate_pct':round(late/len(orders)*100,2),
        'severity':'HIGH' if late>100 else('MEDIUM' if late>0 else 'LOW'),
        'note':f'{late} orders shipped before order date'})

    contracts['start_date'] = pd.to_datetime(contracts['start_date'], errors='coerce')
    contracts['end_date']   = pd.to_datetime(contracts['end_date'],   errors='coerce')
    bad = (contracts['end_date'] < contracts['start_date']).sum()
    results.append({'check_category':'Timeliness','check_name':'Contract end before start',
        'table':'contracts','field':'end_date','issue_count':int(bad),
        'issue_rate_pct':round(bad/len(contracts)*100,2),
        'severity':'HIGH' if bad>0 else 'LOW','note':f'{bad} contracts with end before start'})

    # WRITE
    df_out = pd.DataFrame(results)
    df_out.to_sql("quality_report", conn, if_exists="replace", index=False)
    df_out.to_csv(PROJECT_ROOT / "outputs" / "quality_report.csv", index=False)

    print("\n=== DATA QUALITY REPORT ===")
    print(df_out[['check_category','check_name','issue_count','severity']].to_string(index=False))
    print(f"\nChecks: {len(df_out)} | HIGH: {(df_out['severity']=='HIGH').sum()} | MEDIUM: {(df_out['severity']=='MEDIUM').sum()} | LOW: {(df_out['severity']=='LOW').sum()}")
    conn.close()

if __name__ == "__main__":
    run_checks()