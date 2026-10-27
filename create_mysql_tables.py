
from pathlib import Path
import pandas as pd
import mysql.connector
from getpass import getpass

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "final"

# Connect to your local MySQL server.
# It will prompt you for your MySQL root password.

password = getpass("Enter your MySQL root password: ")

conn = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password=password,
    database="ecommerce_intelligence"
)

cursor = conn.cursor()

def mysql_type(column, series):
    name = column.lower()

    # Identifiers must remain strings, not numbers.
    if name.endswith("_id") or "zip_code_prefix" in name:
        return "VARCHAR(64)"

    if name.endswith("_timestamp") or name.endswith("_at"):
        return "DATETIME"

    if name in ("delivery_days",):
        return "DECIMAL(10,2)"

    if name in ("price", "freight_value", "payment_value",
                "item_subtotal", "item_total_with_freight"):
        return "DECIMAL(12,2)"

    if pd.api.types.is_integer_dtype(series):
        return "BIGINT"

    if pd.api.types.is_float_dtype(series):
        return "DOUBLE"

    return "TEXT"

for file in sorted(DATA.glob("*.csv")):
    df = pd.read_csv(file, low_memory=False)
    table = file.stem

    columns = []
    for col in df.columns:
        col_type = mysql_type(col, df[col])
        safe_col = f"`{col.replace('`', '``')}`"
        columns.append(f"{safe_col} {col_type} NULL")

    sql = (
        f"CREATE TABLE IF NOT EXISTS `{table}` "
        f"({', '.join(columns)})"
    )

    cursor.execute(sql)
    print(f"Created/checked table: {table} ({len(df.columns)} columns)")

conn.commit()
cursor.close()
conn.close()

print("\nAll 9 table schemas created or checked successfully.")
