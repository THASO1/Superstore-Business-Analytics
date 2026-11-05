"""Rebuild the Superstore processed dataset and its core figures.

Run from the project root with: python src/run_analysis.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = PROJECT_ROOT / "data" / "raw" / "sample_superstore_2019.xls"
PROCESSED_FILE = PROJECT_ROOT / "data" / "processed" / "cleaned_superstore_data.csv"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"


def prepare_data() -> pd.DataFrame:
    """Load, clean, and enrich the supplied Orders worksheet."""
    data = pd.read_excel(SOURCE_FILE, sheet_name="Orders")
    data.columns = (
        data.columns.str.strip().str.lower().str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )
    data = data.drop_duplicates().copy()
    data["postal_code"] = data["postal_code"].fillna(5401).astype(int)

    for column in ("sales", "profit"):
        first_quartile, third_quartile = data[column].quantile([0.25, 0.75])
        iqr = third_quartile - first_quartile
        data[column] = data[column].clip(
            lower=first_quartile - 1.5 * iqr,
            upper=third_quartile + 1.5 * iqr,
        )

    data["shipping_duration"] = (data["ship_date"] - data["order_date"]).dt.days
    data["profit_margin"] = np.where(
        data["sales"].ne(0), data["profit"].div(data["sales"]).mul(100), np.nan
    )
    data["sales_performance"] = pd.cut(
        data["sales"],
        bins=[0, 50, 200, float("inf")],
        labels=["Low", "Medium", "High"],
        include_lowest=True,
    )
    return data


def save_figure(filename: str) -> None:
    """Save and close the current matplotlib figure consistently."""
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / filename, bbox_inches="tight", dpi=150)
    plt.close()


def create_figures(data: pd.DataFrame) -> None:
    """Generate the core business-analysis charts."""
    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(10, 5))
    sns.histplot(data["sales"], bins=60, kde=True, color="steelblue")
    plt.title("Distribution of Sales")
    plt.xlabel("Sales ($)")
    save_figure("distribution_of_sales.png")

    category_sales = data.groupby("category", as_index=False)["sales"].sum()
    plt.figure(figsize=(8, 5))
    sns.barplot(category_sales, x="category", y="sales", hue="category", legend=False)
    plt.title("Total Sales by Category")
    plt.ylabel("Total Sales ($)")
    save_figure("total_sales_by_category.png")

    category_profit = data.groupby("category", as_index=False)["profit"].sum()
    plt.figure(figsize=(8, 5))
    sns.barplot(category_profit, x="category", y="profit", hue="category", legend=False)
    plt.title("Total Profit by Category")
    plt.ylabel("Total Profit ($)")
    save_figure("total_profit_by_category.png")

    top_products = data.groupby("product_name", as_index=False)["sales"].sum().nlargest(10, "sales")
    plt.figure(figsize=(10, 6))
    sns.barplot(top_products, y="product_name", x="sales", hue="product_name", legend=False)
    plt.title("Top 10 Products by Sales")
    plt.xlabel("Total Sales ($)")
    plt.ylabel("")
    save_figure("top_10_products_by_sales.png")

    monthly_sales = data.set_index("order_date")["sales"].resample("ME").sum().reset_index()
    plt.figure(figsize=(12, 5))
    sns.lineplot(monthly_sales, x="order_date", y="sales", color="purple", marker="o")
    plt.title("Sales Trend Over Time")
    plt.xlabel("Order Date")
    plt.ylabel("Total Sales ($)")
    save_figure("sales_trend_over_time.png")


def print_kpis(data: pd.DataFrame) -> None:
    """Print a concise, reproducible executive KPI summary."""
    total_sales = data["sales"].sum()
    total_profit = data["profit"].sum()
    print("Executive KPI Summary")
    print(f"Total Sales: ${total_sales:,.2f}")
    print(f"Total Profit: ${total_profit:,.2f}")
    print(f"Overall Profit Margin: {total_profit / total_sales:.2%}")
    print(f"Unique Orders: {data['order_id'].nunique():,}")
    print(f"Average Shipping Duration: {data['shipping_duration'].mean():.2f} days")


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = prepare_data()
    data.to_csv(PROCESSED_FILE, index=False)
    create_figures(data)
    print_kpis(data)


if __name__ == "__main__":
    main()
