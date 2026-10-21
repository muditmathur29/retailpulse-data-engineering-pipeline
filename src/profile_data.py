
from pathlib import Path

import pandas as pd


# Locate the project directories
ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
REPORT_DIR = ROOT / "reports"

REPORT_DIR.mkdir(parents=True, exist_ok=True)


def profile_dataset(name, df):
    """Generate a basic data-quality profile for a DataFrame."""

    report = [
        f"\n{'=' * 50}",
        f"DATASET: {name.upper()}",
        f"{'=' * 50}",
        f"Rows: {df.shape[0]}",
        f"Columns: {df.shape[1]}",
        f"Duplicate rows: {df.duplicated().sum()}",
        "\nColumn data types:",
        df.dtypes.to_string(),
        "\nMissing values per column:",
        df.isna().sum().to_string(),
        "\nUnique values per column:",
        df.nunique().to_string(),
        "\nSample records:",
        df.head().to_string(index=False),
    ]

    return "\n".join(report)


def main():
    datasets = {
        "customers": pd.read_csv(RAW_DIR / "customers.csv"),
        "products": pd.read_csv(RAW_DIR / "products.csv"),
        "orders": pd.read_csv(RAW_DIR / "orders.csv"),
    }

    reports = []

    for name, df in datasets.items():
        reports.append(profile_dataset(name, df))

    full_report = "\n".join(reports)

    report_file = REPORT_DIR / "data_profile.txt"
    report_file.write_text(full_report, encoding="utf-8")

    print(full_report)
    print(f"\nReport saved to: {report_file}")


if __name__ == "__main__":
    main()
