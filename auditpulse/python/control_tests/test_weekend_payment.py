import pandas as pd

TEST_ID   = "CT004"
TEST_NAME = "Weekend Payment"
SEVERITY  = "MEDIUM"
RISK      = "Payments processed outside business hours — reduced oversight"
LOGIC     = "order_date falls on Saturday or Sunday (UAE weekend)"

# UAE public holidays 2022-2024 (sample)
UAE_HOLIDAYS = pd.to_datetime([
    '2022-12-01','2022-12-02','2022-12-03',
    '2023-01-01','2023-04-21','2023-04-22',
    '2023-06-28','2023-09-23','2023-12-01','2023-12-02','2023-12-03',
    '2024-01-01','2024-04-10','2024-06-17','2024-09-22','2024-12-01','2024-12-02','2024-12-03',
])

def run(orders):
    orders = orders.copy()
    orders['order_date'] = pd.to_datetime(orders['order_date'], errors='coerce')

    is_weekend = orders['order_date'].dt.dayofweek.isin([5, 6])  # Sat=5, Sun=6
    is_holiday = orders['order_date'].isin(UAE_HOLIDAYS)

    exceptions = orders[is_weekend | is_holiday].copy()
    exceptions['test_id']           = TEST_ID
    exceptions['test_name']         = TEST_NAME
    exceptions['severity']          = SEVERITY
    exceptions['issue_description'] = 'Order placed on UAE weekend or public holiday'

    return exceptions[['test_id','test_name','severity','order_id',
                        'order_date','sales_amount','issue_description']]