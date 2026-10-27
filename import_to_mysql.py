
from pathlib import Path
from getpass import getpass
import pandas as pd
import mysql.connector

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "final"

password = getpass("Enter your MySQL root password: ")

conn = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password=password,
    database="ecommerce_intelligence"
)

cursor = conn.cursor()

for file in sorted(DATA.glob("*.csv")):
    table = file.stem
    df = pd.read_csv(file, low_memory=False)

    # Convert pandas missing values to Python None for SQL NULL.
    df = df.astype(object).where(pd.notna(df), None)

    columns = list(df.columns)
    column_sql = ", ".join(f"`{c}`" for c in columns)
    placeholders = ", ".join(["%s"] * len(columns))

    insert_sql = (
        f"INSERT INTO `{table}` ({column_sql}) "
        f"VALUES ({placeholders})"
    )

    # Clear this table so rerunning the script doesn't duplicate rows.
    cursor.execute(f"DELETE FROM `{table}`")
    conn.commit()

    batch_size = 1000
    inserted = 0

    for start in range(0, len(df), batch_size):
        batch = df.iloc[start:start + batch_size]
        rows = [tuple(row) for row in batch.itertuples(index=False, name=None)]

        cursor.executemany(insert_sql, rows)
        conn.commit()
        inserted += len(rows)

    print(f"{table}: imported {inserted:,} rows")

cursor.close()
conn.close()

print("\nImport completed.")
