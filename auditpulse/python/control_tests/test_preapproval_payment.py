import pandas as pd

TEST_ID   = "CT003"
TEST_NAME = "Pre-Approval Payment"
SEVERITY  = "HIGH"
RISK      = "Payment processed before formal approval — control bypass"
LOGIC     = "order_date is earlier than approval_date for matched transaction refs"

def run(orders, approvals):
    orders    = orders.copy()
    approvals = approvals.copy()

    orders['order_date']       = pd.to_datetime(orders['order_date'],    errors='coerce')
    approvals['approval_date'] = pd.to_datetime(approvals['approval_date'], errors='coerce')

    # Simulate linkage: match on row index (in real ETL this would be a foreign key)
    orders    = orders.reset_index(drop=True)
    approvals = approvals.reset_index(drop=True)
    min_len   = min(len(orders), len(approvals))

    merged = orders.iloc[:min_len].copy()
    merged['approval_date']  = approvals['approval_date'].iloc[:min_len].values
    merged['approved_amount']= approvals['approved_amount'].iloc[:min_len].values

    mask       = merged['order_date'] < merged['approval_date']
    exceptions = merged[mask].copy()
    exceptions['test_id']           = TEST_ID
    exceptions['test_name']         = TEST_NAME
    exceptions['severity']          = SEVERITY
    exceptions['issue_description'] = 'Order date is before approval date — possible pre-approval payment'

    return exceptions[['test_id','test_name','severity','order_id',
                        'order_date','approval_date','sales_amount','issue_description']].head(500)