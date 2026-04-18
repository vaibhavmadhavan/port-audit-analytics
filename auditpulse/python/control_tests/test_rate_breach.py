import pandas as pd

TEST_ID   = "CT002"
TEST_NAME = "Contract Rate Breach"
SEVERITY  = "HIGH"
RISK      = "Vendor billing above contracted rate"
LOGIC     = "Order unit_price exceeds approved_rate_aed by more than 5% tolerance"

def run(orders, contracts):
    merged = orders.merge(
        contracts[['vendor_id','approved_rate_aed','max_value_aed']],
        how='cross'
    )
    merged['rate_breach'] = merged['unit_price'] > merged['approved_rate_aed'] * 1.05

    exceptions = merged[merged['rate_breach']].copy()
    exceptions['test_id']           = TEST_ID
    exceptions['test_name']         = TEST_NAME
    exceptions['severity']          = SEVERITY
    exceptions['issue_description'] = 'Unit price exceeds approved contract rate by >5%'

    return exceptions[['test_id','test_name','severity','order_id',
                        'unit_price','approved_rate_aed','issue_description']].head(500)