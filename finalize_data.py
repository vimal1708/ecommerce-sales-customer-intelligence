
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
FINAL = ROOT / "data" / "final"
REPORTS = ROOT / "data" / "reports"

FINAL.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

# Load processed tables and save final versions
tables = {}

for file in PROCESSED.glob("*.csv"):
    tables[file.stem] = pd.read_csv(file)

# 1. Products: use an explicit category label for reporting
products = tables["olist_products_dataset"]
products["product_category_name"] = (
    products["product_category_name"].fillna("Unknown")
)
tables["olist_products_dataset"] = products

# 2. Reviews: missing comments are allowed; do not remove rows
# Keep the missing comment fields unchanged.

# 3. Orders: missing timestamps remain missing
# Add delivery duration only where both dates exist.
orders = tables["olist_orders_dataset"]

purchase = pd.to_datetime(
    orders["order_purchase_timestamp"], errors="coerce"
)
delivered = pd.to_datetime(
    orders["order_delivered_customer_date"], errors="coerce"
)

orders["delivery_days"] = (
    (delivered - purchase).dt.total_seconds() / 86400
).round(2)

# Avoid interpreting negative durations as valid delivery times.
orders.loc[orders["delivery_days"] < 0, "delivery_days"] = pd.NA

tables["olist_orders_dataset"] = orders

# 4. Order items: calculate item subtotal before freight
items = tables["olist_order_items_dataset"]
items["item_subtotal"] = items["price"]
items["item_total_with_freight"] = items["price"] + items["freight_value"]
tables["olist_order_items_dataset"] = items

# 5. Save all final tables
summary = []

for name, df in tables.items():
    output_path = FINAL / f"{name}.csv"
    df.to_csv(output_path, index=False)

    summary.append({
        "table": name,
        "rows": len(df),
        "columns": len(df.columns),
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "output_file": str(output_path.relative_to(ROOT))
    })

summary_df = pd.DataFrame(summary)
summary_df.to_csv(REPORTS / "final_data_summary.csv", index=False)

print("=== FINAL DATA SUMMARY ===")
print(summary_df.to_string(index=False))
print("\nFinal tables saved in:", FINAL)
print("Summary saved in:", REPORTS / "final_data_summary.csv")
