
from pathlib import Path
import pandas as pd


# --------------------------------------------------
# Project paths
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Clean customers
# --------------------------------------------------

def clean_customers(df):
    df = df.copy()

    # Remove duplicate customer records
    df = df.drop_duplicates(subset=["customer_id"])

    # Handle missing customer names
    df["customer_name"] = (
        df["customer_name"]
        .fillna("Unknown")
        .str.strip()
    )

    # Handle missing and inconsistent city values
    df["city"] = (
        df["city"]
        .fillna("Unknown")
        .str.strip()
        .str.title()
    )

    # Convert signup_date to datetime
    df["signup_date"] = pd.to_datetime(
        df["signup_date"],
        errors="coerce"
    )

    return df


# --------------------------------------------------
# Clean products
# --------------------------------------------------

def clean_products(df):
    df = df.copy()

    # Remove duplicate product records
    df = df.drop_duplicates(subset=["product_id"])

    # Standardize category names
    df["category"] = (
        df["category"]
        .str.strip()
        .str.title()
    )

    # Convert unit_price to numeric
    df["unit_price"] = pd.to_numeric(
        df["unit_price"],
        errors="coerce"
    )

    # Remove invalid or negative prices
    df = df.dropna(subset=["unit_price"])
    df = df[df["unit_price"] >= 0]

    return df


# --------------------------------------------------
# Clean orders
# --------------------------------------------------

def clean_orders(df, valid_customer_ids, valid_product_ids):
    df = df.copy()

    # Convert order_date to datetime
    df["order_date"] = pd.to_datetime(
        df["order_date"],
        errors="coerce"
    )

    # Remove exact duplicate rows
    df = df.drop_duplicates()

    # Remove records with invalid dates
    df = df.dropna(subset=["order_date"])

    # Remove records with missing quantities
    df = df.dropna(subset=["quantity"])

    # Keep only positive quantities
    df = df[df["quantity"] > 0]

    # Keep only non-negative unit prices
    df = df[df["unit_price"] >= 0]

    # Keep orders linked to valid customers
    df = df[df["customer_id"].isin(valid_customer_ids)]

    # Keep orders linked to valid products
    df = df[df["product_id"].isin(valid_product_ids)]

    # Keep one record per order_id
    df = df.drop_duplicates(
        subset=["order_id"],
        keep="first"
    )

    # Recalculate total amount
    df["total_amount"] = (
        df["quantity"] * df["unit_price"]
    ).round(2)

    return df


# --------------------------------------------------
# Main pipeline
# --------------------------------------------------

def main():

    # ==============================================
    # Customers
    # ==============================================

    customers = pd.read_csv(
        RAW_DIR / "customers.csv"
    )

    print("\n--- Customers Before Cleaning ---")
    print(f"Rows: {len(customers)}")
    print(
        "Missing cities:",
        customers["city"].isna().sum()
    )
    print(
        "Duplicate customer IDs:",
        customers["customer_id"].duplicated().sum()
    )

    cleaned_customers = clean_customers(customers)

    print("\n--- Customers After Cleaning ---")
    print(f"Rows: {len(cleaned_customers)}")
    print(
        "Missing cities:",
        cleaned_customers["city"].isna().sum()
    )
    print(
        "Duplicate customer IDs:",
        cleaned_customers["customer_id"].duplicated().sum()
    )

    customers_output = (
        PROCESSED_DIR / "customers_cleaned.csv"
    )

    cleaned_customers.to_csv(
        customers_output,
        index=False
    )

    print(f"Cleaned customers saved to: {customers_output}")

    # ==============================================
    # Products
    # ==============================================

    products = pd.read_csv(
        RAW_DIR / "products.csv"
    )

    print("\n--- Products Before Cleaning ---")
    print(f"Rows: {len(products)}")
    print(
        "Duplicate product IDs:",
        products["product_id"].duplicated().sum()
    )
    print(
        "Categories:",
        products["category"].unique()
    )

    cleaned_products = clean_products(products)

    print("\n--- Products After Cleaning ---")
    print(f"Rows: {len(cleaned_products)}")
    print(
        "Duplicate product IDs:",
        cleaned_products["product_id"].duplicated().sum()
    )
    print(
        "Categories:",
        cleaned_products["category"].unique()
    )
    print(
        "Missing prices:",
        cleaned_products["unit_price"].isna().sum()
    )

    products_output = (
        PROCESSED_DIR / "products_cleaned.csv"
    )

    cleaned_products.to_csv(
        products_output,
        index=False
    )

    print(f"Cleaned products saved to: {products_output}")

    # ==============================================
    # Orders
    # ==============================================

    orders = pd.read_csv(
        RAW_DIR / "orders.csv"
    )

    print("\n--- Orders Before Cleaning ---")
    print(f"Rows: {len(orders)}")
    print(
        "Duplicate order IDs:",
        orders["order_id"].duplicated().sum()
    )
    print(
        "Missing quantities:",
        orders["quantity"].isna().sum()
    )

    # IDs from the cleaned dimension datasets
    valid_customer_ids = set(
        cleaned_customers["customer_id"]
    )

    valid_product_ids = set(
        cleaned_products["product_id"]
    )

    cleaned_orders = clean_orders(
        orders,
        valid_customer_ids,
        valid_product_ids
    )

    print("\n--- Orders After Cleaning ---")
    print(f"Rows: {len(cleaned_orders)}")
    print(
        "Duplicate order IDs:",
        cleaned_orders["order_id"].duplicated().sum()
    )
    print(
        "Missing order dates:",
        cleaned_orders["order_date"].isna().sum()
    )
    print(
        "Missing quantities:",
        cleaned_orders["quantity"].isna().sum()
    )
    print(
        "Invalid customer references:",
        (~cleaned_orders["customer_id"].isin(
            valid_customer_ids
        )).sum()
    )
    print(
        "Invalid product references:",
        (~cleaned_orders["product_id"].isin(
            valid_product_ids
        )).sum()
    )

    orders_output = (
        PROCESSED_DIR / "orders_cleaned.csv"
    )

    cleaned_orders.to_csv(
        orders_output,
        index=False
    )

    print(f"Cleaned orders saved to: {orders_output}")


# --------------------------------------------------
# Run the pipeline
# --------------------------------------------------

if __name__ == "__main__":
    main()
