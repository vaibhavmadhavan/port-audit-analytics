import pandas as pd
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "DataCoSupplyChainDataset.csv"
DB_FILE = PROJECT_ROOT / "auditpulse.db"

def load_dataco():
    df = pd.read_csv(RAW_FILE, encoding="latin1")
    return df

def main():
    conn = sqlite3.connect(DB_FILE)
    df = load_dataco()
    df.to_sql("bronze_dataco_orders", conn, if_exists="replace", index=False)
    print(f"Loaded {len(df)} rows into bronze_dataco_orders")

    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print("Tables in DB:", cur.fetchall())
    conn.close()

if __name__ == "__main__":
    main()