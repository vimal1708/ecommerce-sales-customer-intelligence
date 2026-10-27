
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "archive"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
REPORT_DIR = PROJECT_DIR / "data" / "reports"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

DATE_COLUMNS = {
    "shipping_limit_date",
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
    "review_creation_date",
    "review_answer_timestamp",
}

ZIP_COLUMNS = {
    "customer_zip_code_prefix",
    "seller_zip_code_prefix",
    "geolocation_zip_code_prefix",
}

summary = []

for file_path in sorted(RAW_DIR.glob("*.csv")):
    print(f"\nProcessing: {file_path.name}")

    df = pd.read_csv(file_path)
    original_rows = len(df)

    # Standardize column names
    df.columns = df.columns.str.strip()

    # Remove unwanted whitespace from text values
    text_columns = df.select_dtypes(include=["object"]).columns

    for col in text_columns:
        df[col] = df[col].map(
            lambda value: value.strip()
            if isinstance(value, str) else value
        )

        # Treat empty strings as missing values
        df[col] = df[col].replace("", pd.NA)

    missing_before = int(df.isna().sum().sum())

    # Convert date columns without deleting invalid records
    converted_dates = []

    for col in df.columns:
        if col in DATE_COLUMNS:
            parsed = pd.to_datetime(df[col], errors="coerce")

            # Count non-empty values that failed conversion
            invalid = int(
                (df[col].notna() & parsed.isna()).sum()
            )

            df[col] = parsed
            converted_dates.append((col, invalid))

    # Preserve postal-code prefixes as text with leading zeros
    for col in ZIP_COLUMNS.intersection(df.columns):
        values = df[col].astype("string").str.strip()
        values = values.str.replace(r"\.0$", "", regex=True)
        df[col] = values.str.zfill(5)

    # Remove exact duplicate records only from geolocation.
    # Other tables require separate key and business-rule checks.
    duplicates_removed = 0

    if file_path.name == "olist_geolocation_dataset.csv":
        duplicates_removed = int(df.duplicated().sum())
        df = df.drop_duplicates()

    output_path = PROCESSED_DIR / file_path.name
    df.to_csv(output_path, index=False, date_format="%Y-%m-%d %H:%M:%S")

    summary.append({
        "file": file_path.name,
        "original_rows": original_rows,
        "processed_rows": len(df),
        "rows_removed": original_rows - len(df),
        "duplicates_removed": duplicates_removed,
        "missing_values_before": missing_before,
        "missing_values_after": int(df.isna().sum().sum()),
        "date_conversion_issues": sum(n for _, n in converted_dates),
    })

    print(f"Original rows: {original_rows:,}")
    print(f"Processed rows: {len(df):,}")
    print(f"Exact duplicates removed: {duplicates_removed:,}")
    print(f"Missing values before: {missing_before:,}")
    print(f"Missing values after: {int(df.isna().sum().sum()):,}")

    if converted_dates:
        print("Date conversion issues:", converted_dates)

report = pd.DataFrame(summary)
report_path = REPORT_DIR / "cleaning_summary.csv"
report.to_csv(report_path, index=False)

print("\n" + "=" * 55)
print("INITIAL CLEANING COMPLETED")
print(f"Processed files: {len(summary)}")
print(f"Cleaning report: {report_path}")
print("=" * 55)
