
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "final"
REPORTS = ROOT / "data" / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

tables = {
    file.stem: pd.read_csv(file)
    for file in DATA.glob("*.csv")
}

checks = []

def record(name, passed, details):
    checks.append({
        "check": name,
        "status": "PASS" if passed else "FAIL",
        "details": details
    })
    print(f"[{'PASS' if passed else 'FAIL'}] {name}: {details}")

customers = tables["olist_customers_dataset"]
orders = tables["olist_orders_dataset"]
items = tables["olist_order_items_dataset"]
payments = tables["olist_order_payments_dataset"]
reviews = tables["olist_order_reviews_dataset"]
products = tables["olist_products_dataset"]
sellers = tables["olist_sellers_dataset"]

# 1. Primary keys
for df, column, name in [
    (orders, "order_id", "Orders"),
    (customers, "customer_id", "Customers"),
    (products, "product_id", "Products"),
    (sellers, "seller_id", "Sellers"),
]:
    valid = df[column].notna().all() and df[column].is_unique
    record(f"{name} primary key", valid,
           f"{column} non-null and unique")

# 2. Foreign-key relationships
relationships = [
    (items, "order_id", orders, "order_id", "Items -> Orders"),
    (payments, "order_id", orders, "order_id", "Payments -> Orders"),
    (reviews, "order_id", orders, "order_id", "Reviews -> Orders"),
    (orders, "customer_id", customers, "customer_id", "Orders -> Customers"),
    (items, "product_id", products, "product_id", "Items -> Products"),
    (items, "seller_id", sellers, "seller_id", "Items -> Sellers"),
]

for child, child_col, parent, parent_col, name in relationships:
    unmatched = (
        child[child_col].notna()
        & ~child[child_col].isin(parent[parent_col])
    ).sum()
    record(name, unmatched == 0, f"{unmatched} unmatched rows")

# 3. Business rules
record(
    "Non-negative item prices",
    (items["price"] >= 0).all(),
    "All item prices are >= 0"
)

record(
    "Non-negative freight",
    (items["freight_value"] >= 0).all(),
    "All freight values are >= 0"
)

record(
    "Payment values non-negative",
    (payments["payment_value"] >= 0).all(),
    "All payment values are >= 0"
)

record(
    "Review scores in range",
    reviews["review_score"].between(1, 5).all(),
    "Scores are between 1 and 5"
)

record(
    "Product category populated",
    products["product_category_name"].notna().all(),
    "Missing categories represented by Unknown"
)

# 4. Derived calculations
expected_total = items["price"] + items["freight_value"]
record(
    "Item total calculation",
    (items["item_total_with_freight"] - expected_total).abs().lt(0.001).all(),
    "item_total_with_freight = price + freight_value"
)

purchase = pd.to_datetime(
    orders["order_purchase_timestamp"], errors="coerce"
)
delivered = pd.to_datetime(
    orders["order_delivered_customer_date"], errors="coerce"
)
expected_days = (delivered - purchase).dt.total_seconds() / 86400
valid_days = expected_days.notna() & (expected_days >= 0)

delivery_check = (
    orders.loc[valid_days, "delivery_days"]
    .sub(expected_days.loc[valid_days])
    .abs()
    .lt(0.02)
    .all()
)
record(
    "Delivery duration calculation",
    delivery_check,
    "Delivery days agree with available timestamps"
)

# 5. Save report
report = pd.DataFrame(checks)
report.to_csv(REPORTS / "final_validation_report.csv", index=False)

print("\n=== FINAL VALIDATION SUMMARY ===")
print(report["status"].value_counts().to_string())
print("\nReport saved to:", REPORTS / "final_validation_report.csv")
