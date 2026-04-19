import pandas as pd

TEST_ID   = "CT007"
TEST_NAME = "TEU Volume Mismatch"
SEVERITY  = "HIGH"
RISK      = "Vendor billing for more TEU volume than terminal actually processed — overbilling"
LOGIC     = "Aggregated order quantity per region per month exceeds terminal teu_actual for that period"

def run(orders, throughput):
    orders     = orders.copy()
    throughput = throughput.copy()

    orders['order_date'] = pd.to_datetime(orders['order_date'], errors='coerce')
    orders['year']       = orders['order_date'].dt.year
    orders['month']      = orders['order_date'].dt.month

    # Aggregate billed quantity per region per month
    billed = (
        orders.groupby(['order_region','year','month'])['quantity']
        .sum()
        .reset_index()
        .rename(columns={'quantity':'billed_quantity', 'order_region':'region'})
    )

    merged = billed.merge(
        throughput[['region','year','month','teu_actual']],
        on=['region','year','month'],
        how='inner'
    )

    # Flag where billed quantity exceeds actual TEU by more than 2%
    merged['variance_pct'] = ((merged['billed_quantity'] - merged['teu_actual'])
                               / merged['teu_actual'] * 100).round(2)
    exceptions = merged[merged['billed_quantity'] > merged['teu_actual'] * 1.02].copy()
    exceptions['test_id']           = TEST_ID
    exceptions['test_name']         = TEST_NAME
    exceptions['severity']          = SEVERITY
    exceptions['issue_description'] = 'Billed quantity exceeds terminal TEU throughput by >2%'

    return exceptions[['test_id','test_name','severity','region','year','month',
                        'billed_quantity','teu_actual','variance_pct','issue_description']]