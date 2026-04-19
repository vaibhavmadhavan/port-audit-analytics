import pandas as pd

TEST_ID   = "CT005"
TEST_NAME = "New Vendor Risk"
SEVERITY  = "HIGH"
RISK      = "Payments to recently registered vendors — insufficient due diligence window"
LOGIC     = "Vendor registered less than 30 days before the order date, order value above AED 5,000"

def run(orders, vendors):
    orders  = orders.copy()
    vendors = vendors.copy()

    orders['order_date']         = pd.to_datetime(orders['order_date'], errors='coerce')
    vendors['registration_date'] = pd.to_datetime(vendors['registration_date'], errors='coerce')

    # Cross join orders with vendors then filter
    orders['_key']  = 1
    vendors['_key'] = 1
    merged = orders.merge(vendors, on='_key').drop(columns='_key')

    merged['days_since_reg'] = (merged['order_date'] - merged['registration_date']).dt.days

    mask = (
        (merged['days_since_reg'] >= 0) &
        (merged['days_since_reg'] < 30) &
        (merged['sales_amount'] > 5000)
    )
    exceptions = merged[mask].copy()
    exceptions['test_id']           = TEST_ID
    exceptions['test_name']         = TEST_NAME
    exceptions['severity']          = SEVERITY
    exceptions['issue_description'] = (
        'Order placed within 30 days of vendor registration with value > AED 5,000'
    )

    return exceptions[['test_id','test_name','severity','order_id','vendor_id',
                        'vendor_name','sales_amount','order_date',
                        'registration_date','days_since_reg',
                        'issue_description']].head(500)