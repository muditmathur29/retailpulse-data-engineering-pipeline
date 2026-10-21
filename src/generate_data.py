
from pathlib import Path

import numpy as np
import pandas as pd


# Find the project's root directory
ROOT = Path(__file__).resolve().parents[1]

# Create the raw data directory if it doesn't exist
RAW_DIR = ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Make generated data reproducible
rng = np.random.default_rng(42)

# Generate 500 customers
n_customers = 500

customers = pd.DataFrame({
    "customer_id": np.arange(1, n_customers + 1),
    "customer_name": [
        f"Customer_{i}" for i in range(1, n_customers + 1)
    ],
    "city": rng.choice(
        ["Jaipur", "Delhi", "Mumbai", "Pune", "Bengaluru"],
        size=n_customers
    ),
    "signup_date": rng.choice(
        pd.date_range("2025-01-01", "2026-09-30"),
        size=n_customers
    )
})

# Introduce missing cities to simulate imperfect raw data
missing_indices = rng.choice(
    customers.index,
    size=15,
    replace=False
)

customers.loc[missing_indices, "city"] = None

# Save the raw dataset
output_file = RAW_DIR / "customers.csv"
customers.to_csv(output_file, index=False)

print("Customer data generated successfully!")
print(f"Total customers: {len(customers)}")
print(f"Missing cities: {customers['city'].isna().sum()}")
print(f"Saved to: {output_file}") 



# -------------------------
# Generate product data
# -------------------------

n_products = 50

products = pd.DataFrame({
    "product_id": np.arange(1, n_products + 1),
    "product_name": [
        f"Product_{i}" for i in range(1, n_products + 1)
    ],
    "category": rng.choice(
        ["Electronics", "Clothing", "Home", "Books"],
        size=n_products
    ),
    "unit_price": np.round(
        rng.uniform(100, 20000, size=n_products), 2
    )
})

# Introduce inconsistent category formatting
products.loc[0:4, "category"] = " electronics "

products.to_csv(RAW_DIR / "products.csv", index=False)


# -------------------------
# Generate order data
# -------------------------

n_orders = 5000

orders = pd.DataFrame({
    "order_id": np.arange(1, n_orders + 1),
    "customer_id": rng.integers(
        1, n_customers + 1, size=n_orders
    ),
    "product_id": rng.integers(
        1, n_products + 1, size=n_orders
    ),
    "order_date": rng.choice(
        pd.date_range("2025-01-01", "2026-10-15"),
        size=n_orders
    ),
    "quantity": rng.integers(1, 6, size=n_orders)
})

# Attach the product prices to orders
orders = orders.merge(
    products[["product_id", "unit_price"]],
    on="product_id",
    how="left"
)

# Calculate order amounts
orders["total_amount"] = (
    orders["quantity"] * orders["unit_price"]
).round(2)


# -------------------------
# Introduce data-quality issues
# -------------------------

# Missing quantities
missing_order_indices = rng.choice(
    orders.index, size=20, replace=False
)
orders.loc[missing_order_indices, "quantity"] = np.nan

# Invalid negative quantities
invalid_order_indices = rng.choice(
    orders.index, size=10, replace=False
)
orders.loc[invalid_order_indices, "quantity"] = -1

# Duplicate 25 order records
orders = pd.concat(
    [orders, orders.iloc[:25]],
    ignore_index=True
)

# Introduce one invalid date
orders["order_date"] = orders["order_date"].astype(str)
orders.loc[0, "order_date"] = "not-a-date"

orders.to_csv(RAW_DIR / "orders.csv", index=False)


# -------------------------
# Print dataset summaries
# -------------------------

print("\nAll raw datasets generated successfully!")
print(f"Customers: {len(customers)}")
print(f"Products:  {len(products)}")
print(f"Orders:    {len(orders)}")
print(f"Raw data directory: {RAW_DIR}")

