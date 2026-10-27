
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data" / "processed"
REPORT_DIR = PROJECT_DIR / "data" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

issues = []


def record(check, status, details):
    issues.append({
        "check": check,
        "status": status,
        "details": str(details)
    })
    print(f"[{status}] {check}: {details}")


def load(name):
    path = DATA_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing processed file: {path}")
    return pd.read_csv(path)


# Load the main tables
orders = load("olist_orders_dataset.csv")
customers = load("olist_customers_dataset.csv")
items = load("olist_order_items_dataset.csv")
payments = load("olist_order_payments_dataset.csv")
reviews = load("olist_order_reviews_dataset.csv")
products = load("olist_products_dataset.csv")
sellers = load("olist_sellers_dataset.csv")
geo = load("olist_geolocation_dataset.csv")

print("\n=== E-COMMERCE DATA QUALITY VALIDATION ===\n")

# 1. Required key columns
key_checks = [
    ("orders.order_id", orders, "order_id"),
    ("customers.customer_id", customers, "customer_id"),
    ("products.product_id", products, "product_id"),
    ("sellers.seller_id", sellers, "seller_id"),
]

for name, df, col in key_checks:
    record(
        f"{name} unique and non-null",
        "PASS" if df[col].notna().all() and not df[col].duplicated().any() else "CHECK",
        f"nulls={df[col].isna().sum()}, duplicate_keys={df[col].duplicated().sum()}"
    )

# 2. Missing values
for name, df in [
    ("orders", orders),
    ("customers", customers),
    ("items", items),
    ("payments", payments),
    ("reviews", reviews),
    ("products", products),
    ("sellers", sellers),
    ("geolocation", geo),
]:
    missing = int(df.isna().sum().sum())
    record(
        f"{name}: missing values",
        "PASS" if missing == 0 else "INFO",
        f"{missing} missing cells; review column-level report"
    )

# 3. Referential integrity
checks = [
    ("items.order_id -> orders", items, "order_id", orders, "order_id"),
    ("payments.order_id -> orders", payments, "order_id", orders, "order_id"),
    ("reviews.order_id -> orders", reviews, "order_id", orders, "order_id"),
    ("orders.customer_id -> customers", orders, "customer_id", customers, "customer_id"),
    ("items.product_id -> products", items, "product_id", products, "product_id"),
    ("items.seller_id -> sellers", items, "seller_id", sellers, "seller_id"),
]

for name, child, child_col, parent, parent_col in checks:
    unmatched = int(
        (~child[child_col].isin(parent[parent_col])).sum()
    )
    record(
        name,
        "PASS" if unmatched == 0 else "CHECK",
        f"{unmatched} unmatched rows"
    )

# 4. Numeric business rules
for col in ["price", "freight_value"]:
    invalid = int((items[col] < 0).sum())
    record(
        f"Order items: {col} non-negative",
        "PASS" if invalid == 0 else "CHECK",
        f"{invalid} negative values"
    )

invalid_payment = int((payments["payment_value"] < 0).sum())
record(
    "Payments: payment_value non-negative",
    "PASS" if invalid_payment == 0 else "CHECK",
    f"{invalid_payment} negative values"
)

invalid_review = int(
    (~reviews["review_score"].between(1, 5)).sum()
)
record(
    "Reviews: score between 1 and 5",
    "PASS" if invalid_review == 0 else "CHECK",
    f"{invalid_review} invalid scores"
)

# 5. Date consistency
date_cols = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

for col in date_cols:
    orders[col] = pd.to_datetime(orders[col], errors="coerce")

invalid_delivery = int(
    (
        orders["order_delivered_customer_date"].notna()
        & (
            orders["order_delivered_customer_date"]
            < orders["order_purchase_timestamp"]
        )
    ).sum()
)

record(
    "Orders: delivery not before purchase",
    "PASS" if invalid_delivery == 0 else "CHECK",
    f"{invalid_delivery} suspicious rows"
)

# 6. Duplicate complete records
for name, df in [
    ("orders", orders),
    ("customers", customers),
    ("items", items),
    ("payments", payments),
    ("reviews", reviews),
    ("products", products),
    ("sellers", sellers),
    ("geolocation", geo),
]:
    count = int(df.duplicated().sum())
    record(
        f"{name}: exact duplicate rows",
        "PASS" if count == 0 else "CHECK",
        f"{count} duplicate rows"
    )

# Save machine-readable validation results
results = pd.DataFrame(issues)
output = REPORT_DIR / "validation_report.csv"
results.to_csv(output, index=False)

print("\nValidation report saved to:", output)
print("\nStatus counts:")
print(results["status"].value_counts().to_string())
