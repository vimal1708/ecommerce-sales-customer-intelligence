
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed"
REPORTS = ROOT / "data" / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

# 1. Investigate delivered orders with missing dates
orders = pd.read_csv(DATA / "olist_orders_dataset.csv")

date_columns = [
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date"
]

print("=== DELIVERED ORDERS WITH MISSING DATES ===")

delivered_missing = orders[
    (orders["order_status"] == "delivered")
    & orders[date_columns].isna().any(axis=1)
]

print("Number of delivered orders with at least one missing date:",
      len(delivered_missing))

print(delivered_missing[
    ["order_id", "order_status", "order_purchase_timestamp"] + date_columns
].head(20).to_string(index=False))

delivered_missing.to_csv(
    REPORTS / "delivered_orders_missing_dates.csv", index=False
)

# 2. Check whether product missing values occur together
products = pd.read_csv(DATA / "olist_products_dataset.csv")

product_columns = [
    "product_category_name",
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
]

print("\n=== PRODUCT MISSINGNESS COMBINATIONS ===")

print(
    products[product_columns]
    .isna()
    .value_counts()
    .head(10)
    .to_string()
)

print("\n=== PRODUCTS WITH MISSING WEIGHT OR DIMENSIONS ===")

dimension_columns = [
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
]

dimension_missing = products[
    products[dimension_columns].isna().any(axis=1)
]

print(dimension_missing[
    ["product_id"] + product_columns
].to_string(index=False))

dimension_missing.to_csv(
    REPORTS / "products_missing_dimensions.csv", index=False
)

print("\nReports saved to:", REPORTS)
