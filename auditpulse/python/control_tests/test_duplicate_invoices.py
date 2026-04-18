import pandas as pd

TEST_ID   = "CT001"
TEST_NAME = "Duplicate Invoices"
SEVERITY  = "HIGH"
RISK      = "Financial leakage through duplicate vendor billing"
LOGIC     = "Same customer_id + sales_amount within 7 days, more than once"

def run(orders):
    orders = orders.copy()
    orders['order_date'] = pd.to_datetime(orders['order_date'], errors='coerce')
    orders = orders.sort_values(['customer_id','sales_amount','order_date'])

    orders['prev_customer']  = orders['customer_id'].shift(1)
    orders['prev_amount']    = orders['sales_amount'].shift(1)
    orders['prev_date']      = orders['order_date'].shift(1)
    orders['days_diff']      = (orders['order_date'] - orders['prev_date']).dt.days

    mask = (
        (orders['customer_id']  == orders['prev_customer']) &
        (orders['sales_amount'] == orders['prev_amount'])   &
        (orders['days_diff'].between(0, 7))
    )
    exceptions = orders[mask].copy()
    exceptions['test_id']          = TEST_ID
    exceptions['test_name']        = TEST_NAME
    exceptions['severity']         = SEVERITY
    exceptions['issue_description']= 'Possible duplicate order: same customer, same amount within 7 days'

    return exceptions[['test_id','test_name','severity','order_id','customer_id',
                        'sales_amount','order_date','issue_description']]