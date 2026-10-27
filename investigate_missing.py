
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "processed"
REPORTS = ROOT / "data" / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

# 1. Missing values in every processed CSV
missing_rows = []

for file in sorted(DATA.glob("*.csv")):
    df = pd.read_csv(file)

    for col in df.columns:
        count = int(df[col].isna().sum())

        if count > 0:
            missing_rows.append({
                "file": file.name,
                "column": col,
                "missing_count": count,
                "missing_percentage": round(
                    count / len(df) * 100, 2
                ) if len(df) else 0
            })

missing_report = pd.DataFrame(missing_rows)
missing_path = REPORTS / "missing_values_by_column.csv"
missing_report.to_csv(missing_path, index=False)

print("=== MISSING VALUES BY COLUMN ===")
if not missing_report.empty:
    print(missing_report.to_string(index=False))
else:
    print("No missing values found.")

# 2. Missing order timestamps by order status
orders = pd.read_csv(DATA / "olist_orders_dataset.csv")

date_columns = [
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
]

print("\n=== MISSING ORDER DATES BY STATUS ===")

for col in date_columns:
    print(f"\nColumn: {col}")

    summary = (
        orders.assign(is_missing=orders[col].isna())
        .groupby(["order_status", "is_missing"])
        .size()
        .unstack(fill_value=0)
    )

    summary = summary.rename(
        columns={False: "present", True: "missing"}
    )

    print(summary.to_string())

    summary.to_csv(
        REPORTS / f"{col}_by_order_status.csv"
    )

# 3. Investigate product attribute missingness
products = pd.read_csv(DATA / "olist_products_dataset.csv")

product_columns = [
    "product_category_name",
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm",
]

print("\n=== PRODUCT MISSINGNESS PATTERNS ===")
print(products[product_columns].isna().sum().to_string())

print("\nRows with missing product category:")
print(
    products.loc[
        products["product_category_name"].isna(),
        ["product_id"] + product_columns
    ].head(10).to_string(index=False)
)

print("\nReports saved in:", REPORTS)
