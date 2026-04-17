import sqlite3
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_FILE = PROJECT_ROOT / "auditpulse.db"
print("DB path:", DB_FILE)  

KEEP_COLUMNS = {
    'Order Id':                     'order_id',
    'Order Customer Id':            'customer_id',
    'order date (DateOrders)':      'order_date',
    'shipping date (DateOrders)':   'ship_date',
    'Order Status':                 'order_status',
    'Shipping Mode':                'shipping_mode',
    'Delivery Status':              'delivery_status',
    'Days for shipping (real)':     'days_shipping_actual',
    'Days for shipment (scheduled)':'days_shipping_scheduled',
    'Late_delivery_risk':           'late_delivery_flag',
    'Sales':                        'sales_amount',
    'Order Item Quantity':          'quantity',
    'Order Item Product Price':     'unit_price',
    'Order Item Discount':          'discount_amount',
    'Order Item Discount Rate':     'discount_rate',
    'Order Item Total':             'line_total',
    'Order Profit Per Order':       'profit',
    'Benefit per order':            'benefit_per_order',
    'Order Item Profit Ratio':      'profit_ratio',
    'Product Name':                 'product_name',
    'Product Price':                'product_price',
    'Category Name':                'category_name',
    'Department Name':              'department_name',
    'Market':                       'market',
    'Order Region':                 'order_region',
    'Order Country':                'order_country',
    'Order City':                   'order_city',
    'Customer Segment':             'customer_segment',
}

def clean():
    conn = sqlite3.connect(DB_FILE)

    df = pd.read_sql("SELECT * FROM bronze_dataco_orders", conn)
    print(f"Bronze rows: {len(df)}")

    df = df[list(KEEP_COLUMNS.keys())].rename(columns=KEEP_COLUMNS)

    # Standardize dates
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    df['ship_date']  = pd.to_datetime(df['ship_date'],  errors='coerce')

    # Standardize strings
    for col in ['order_status', 'shipping_mode', 'delivery_status', 'market',
                'order_region', 'order_country', 'category_name', 'department_name',
                'customer_segment', 'product_name']:
        df[col] = df[col].str.strip().str.title()

    # Numeric cleanup
    for col in ['sales_amount', 'unit_price', 'discount_amount', 'line_total',
                'profit', 'benefit_per_order', 'product_price']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop rows with no order_id or order_date
    before = len(df)
    df = df.dropna(subset=['order_id', 'order_date'])
    print(f"Dropped {before - len(df)} rows missing order_id or order_date")

    # Write silver table
    df.to_sql("silver_orders", conn, if_exists="replace", index=False)
    print(f"Written {len(df)} rows to silver_orders")

    conn.close()

if __name__ == "__main__":
    clean()