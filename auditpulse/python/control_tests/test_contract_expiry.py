import pandas as pd

TEST_ID   = "CT006"
TEST_NAME = "Contract Expiry Bypass"
SEVERITY  = "HIGH"
RISK      = "Services invoiced after contract end date — no valid contract coverage"
LOGIC     = "order_date is after the contract end_date for matched vendor"

def run(orders, contracts):
    orders    = orders.copy()
    contracts = contracts.copy()

    orders['order_date']    = pd.to_datetime(orders['order_date'],  errors='coerce')
    contracts['end_date']   = pd.to_datetime(contracts['end_date'], errors='coerce')
    contracts['start_date'] = pd.to_datetime(contracts['start_date'], errors='coerce')

    # Use cross join then filter by expiry
    orders['_key']    = 1
    contracts['_key'] = 1
    merged = orders.merge(
        contracts[['_key','contract_id','vendor_id','end_date','approved_rate_aed']],
        on='_key'
    ).drop(columns='_key')

    mask = merged['order_date'] > merged['end_date']
    exceptions = merged[mask].copy()
    exceptions['test_id']           = TEST_ID
    exceptions['test_name']         = TEST_NAME
    exceptions['severity']          = SEVERITY
    exceptions['issue_description'] = 'Order date falls after contract expiry date'

    return exceptions[['test_id','test_name','severity','order_id','contract_id',
                        'vendor_id','order_date','end_date',
                        'sales_amount','issue_description']].head(500)