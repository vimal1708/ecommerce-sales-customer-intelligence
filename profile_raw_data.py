
from pathlib import Path
import pandas as pd

# Locate the project and raw data folder
PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_DIR / "data" / "archive"

print("=" * 60)
print("E-COMMERCE RAW DATA PROFILING")
print("=" * 60)

if not RAW_DATA_DIR.exists():
    raise FileNotFoundError(
        f"Data folder not found: {RAW_DATA_DIR}"
    )

csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError(
        "No CSV files found inside data/archive/"
    )

print(f"\nCSV files found: {len(csv_files)}")

for file_path in csv_files:
    print("\n" + "=" * 60)
    print(f"FILE: {file_path.name}")
    print("=" * 60)

    try:
        df = pd.read_csv(file_path)

        print(f"Rows: {df.shape[0]}")
        print(f"Columns: {df.shape[1]}")

        print("\nColumn names:")
        print(df.columns.tolist())

        print("\nData types:")
        print(df.dtypes.to_string())

        print("\nMissing values:")
        print(df.isnull().sum().to_string())

        print("\nDuplicate rows:", df.duplicated().sum())

        print("\nFirst 5 rows:")
        print(df.head().to_string(index=False))

    except Exception as error:
        print(f"Could not inspect this file: {error}")

print("\nRaw data profiling completed.")
