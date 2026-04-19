import pandas as pd

TEST_ID   = "CT008"
TEST_NAME = "Split Billing Detection"
SEVERITY  = "MEDIUM"
RISK      = "Orders split across multiple transactions to stay below approval threshold"
LOGIC     = "Same customer has 3+ orders in the same week with individual amounts below AED 10,000 but combined total above AED 25,000"

SINGLE_THRESHOLD   = 10000   # AED — individual order just below this
COMBINED_THRESHOLD = 25000   # AED — combined weekly total above this
MIN_ORDER_COUNT    = 3       # minimum orders in the week to flag

def run(orders):
    orders = orders.copy()
    orders['order_date'] = pd.to_datetime(orders['order_date'], errors='coerce')
    orders['week']       = orders['order_date'].dt.to_period('W')

    # Only look at orders below the single threshold
    below_threshold = orders[orders['sales_amount'] < SINGLE_THRESHOLD]

    grouped = (
        below_threshold.groupby(['customer_id','week'])
        .agg(
            order_count=('order_id', 'count'),
            combined_total=('sales_amount', 'sum'),
            order_ids=('order_id', lambda x: ', '.join(x.astype(str)))
        )
        .reset_index()
    )

    mask = (
        (grouped['order_count'] >= MIN_ORDER_COUNT) &
        (grouped['combined_total'] > COMBINED_THRESHOLD)
    )
    exceptions = grouped[mask].copy()
    exceptions['test_id']           = TEST_ID
    exceptions['test_name']         = TEST_NAME
    exceptions['severity']          = SEVERITY
    exceptions['issue_description'] = (
        f'{MIN_ORDER_COUNT}+ orders below AED {SINGLE_THRESHOLD:,} in same week, '
        f'combined total exceeds AED {COMBINED_THRESHOLD:,}'
    )

    return exceptions[['test_id','test_name','severity','customer_id','week',
                        'order_count','combined_total','order_ids','issue_description']]