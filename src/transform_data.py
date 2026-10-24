from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def main():
    # Load cleaned datasets
    customers = pd.read_csv(PROCESSED_DIR / "customers_cleaned.csv")
    products = pd.read_csv(PROCESSED_DIR / "products_cleaned.csv")
    orders = pd.read_csv(PROCESSED_DIR / "orders_cleaned.csv")

    print("Customers:", customers.shape)
    print("Products:", products.shape)
    print("Orders:", orders.shape)

    # Customer sales summary
    customer_sales = (
        orders.groupby("customer_id")
        .agg(
            total_orders=("order_id", "count"),
            total_spent=("total_amount", "sum")
        )
        .reset_index()
    )

    # Add customer details
    customer_sales = customer_sales.merge(
        customers,
        on="customer_id",
        how="left"
    )

    # Round total spending
    customer_sales["total_spent"] = customer_sales["total_spent"].round(2)

    # Save the summary
    customer_sales.to_csv(
        PROCESSED_DIR / "customer_sales_summary.csv",
        index=False
    )

    print("\nCustomer sales summary:")
    print(customer_sales.head())
    print("Summary shape:", customer_sales.shape)

        # Product sales summary
    product_sales = (
        orders.groupby("product_id")
        .agg(
            total_quantity_sold=("quantity", "sum"),
            total_revenue=("total_amount", "sum"),
            total_orders=("order_id", "count")
        )
        .reset_index()
    )

    # Add product details
    product_sales = product_sales.merge(
        products,
        on="product_id",
        how="left"
    )

    # Round revenue
    product_sales["total_revenue"] = product_sales["total_revenue"].round(2)

    # Sort by revenue
    product_sales = product_sales.sort_values(
        by="total_revenue",
        ascending=False
    )

    # Save the summary
    product_sales.to_csv(
        PROCESSED_DIR / "product_sales_summary.csv",
        index=False
    )

    print("\nProduct sales summary:")
    print(product_sales.head())
    print("Summary shape:", product_sales.shape)

        # Daily revenue summary
    orders["order_date"] = pd.to_datetime(orders["order_date"])

    daily_revenue = (
        orders.groupby(orders["order_date"].dt.date)
        .agg(
            daily_revenue=("total_amount", "sum"),
            total_orders=("order_id", "count"),
            total_quantity_sold=("quantity", "sum")
        )
        .reset_index()
    )

    # Rename date column
    daily_revenue = daily_revenue.rename(
        columns={"order_date": "date"}
    )

    # Round revenue
    daily_revenue["daily_revenue"] = daily_revenue["daily_revenue"].round(2)

    # Sort by date
    daily_revenue = daily_revenue.sort_values("date")

    # Save the summary
    daily_revenue.to_csv(
        PROCESSED_DIR / "daily_revenue_summary.csv",
        index=False
    )

    print("\nDaily revenue summary:")
    print(daily_revenue.head())
    print("Summary shape:", daily_revenue.shape)

        # Overall business metrics
    total_revenue = orders["total_amount"].sum()
    total_orders = orders["order_id"].nunique()
    total_customers = customers["customer_id"].nunique()
    total_products = products["product_id"].nunique()
    total_quantity_sold = orders["quantity"].sum()
    average_order_value = total_revenue / total_orders

    business_metrics = pd.DataFrame({
        "metric": [
            "Total Revenue",
            "Total Orders",
            "Total Customers",
            "Total Products",
            "Total Quantity Sold",
            "Average Order Value"
        ],
        "value": [
            round(total_revenue, 2),
            total_orders,
            total_customers,
            total_products,
            total_quantity_sold,
            round(average_order_value, 2)
        ]
    })

    # Save business metrics
    business_metrics.to_csv(
        REPORTS_DIR / "business_metrics.csv",
        index=False
    )

    print("\nOverall Business Metrics:")
    print(business_metrics)

        # Validate transformed datasets
    print("\nTransformation Validation:")

    output_files = [
        "customer_sales_summary.csv",
        "product_sales_summary.csv",
        "daily_revenue_summary.csv"
    ]

    for file_name in output_files:
        file_path = PROCESSED_DIR / file_name

        if file_path.exists():
            df = pd.read_csv(file_path)
            print(f"{file_name}: {df.shape} — File exists")
        else:
            print(f"{file_name}: Missing")


if __name__ == "__main__":
    main()