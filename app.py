
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Superstore Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "processed" / "cleaned_superstore_data.csv"


# =========================================================
# CUSTOM STYLING
# =========================================================

st.markdown("""
<style>
    .stApp {
        background-color: #0B1120;
        color: #E2E8F0;
    }

    [data-testid="stSidebar"] {
        background-color: #111827;
    }

    [data-testid="stMetric"] {
        background-color: #172337;
        border: 1px solid #26364D;
        padding: 18px;
        border-radius: 12px;
    }

    [data-testid="stMetricLabel"] {
        color: #94A3B8;
    }

    h1, h2, h3 {
        color: #E2E8F0;
    }

    .subtitle {
        color: #94A3B8;
        font-size: 15px;
        margin-top: -12px;
    }

    hr {
        border-color: #26364D;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# DATA LOADING
# =========================================================

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)

    df["order_date"] = pd.to_datetime(
        df["order_date"], errors="coerce"
    )

    df["ship_date"] = pd.to_datetime(
        df["ship_date"], errors="coerce"
    )

    numeric_columns = [
        "sales", "profit", "quantity",
        "discount", "shipping_duration",
        "profit_margin"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(
        subset=["order_date", "sales", "profit"]
    )

    return df


try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load dataset: {e}")
    st.info(
        "Make sure the processed CSV exists at "
        "data/processed/cleaned_superstore_data.csv"
    )
    st.stop()


# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.title("📊 Superstore Analytics")
st.sidebar.caption("Business Performance Dashboard")

st.sidebar.divider()

st.sidebar.subheader("Filters")

min_date = df["order_date"].min().date()
max_date = df["order_date"].max().date()

date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, (tuple, list)):
    if len(date_range) == 2:
        start_date, end_date = date_range
    elif len(date_range) == 1:
        start_date = end_date = date_range[0]
    else:
        start_date, end_date = min_date, max_date
else:
    start_date = end_date = date_range

regions = sorted(df["region"].dropna().unique())
categories = sorted(df["category"].dropna().unique())
segments = sorted(df["segment"].dropna().unique())
ship_modes = sorted(df["ship_mode"].dropna().unique())

selected_regions = st.sidebar.multiselect(
    "Region",
    regions,
    default=regions
)

selected_categories = st.sidebar.multiselect(
    "Category",
    categories,
    default=categories
)

selected_segments = st.sidebar.multiselect(
    "Customer Segment",
    segments,
    default=segments
)

selected_ship_modes = st.sidebar.multiselect(
    "Shipping Mode",
    ship_modes,
    default=ship_modes
)

st.sidebar.divider()

st.sidebar.caption(
    f"Dataset Records: {len(df):,}"
)


# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df[
    (df["order_date"].dt.date >= start_date)
    & (df["order_date"].dt.date <= end_date)
    & (df["region"].isin(selected_regions))
    & (df["category"].isin(selected_categories))
    & (df["segment"].isin(selected_segments))
    & (df["ship_mode"].isin(selected_ship_modes))
].copy()


if filtered_df.empty:
    st.warning("No records found for the selected filters.")
    st.stop()


# =========================================================
# KPI CALCULATIONS
# =========================================================

total_sales = filtered_df["sales"].sum()
total_profit = filtered_df["profit"].sum()
total_orders = filtered_df["order_id"].nunique()
total_customers = filtered_df["customer_id"].nunique()
total_quantity = filtered_df["quantity"].sum()

profit_margin = (
    (total_profit / total_sales) * 100
    if total_sales != 0 else 0
)

avg_order_value = (
    total_sales / total_orders
    if total_orders != 0 else 0
)


# =========================================================
# HEADER
# =========================================================

st.title("Superstore Business Analytics")

st.markdown(
    '<p class="subtitle">'
    'Explore sales performance, profitability, customer '
    'segments, and operational efficiency.'
    '</p>',
    unsafe_allow_html=True
)

st.divider()


# =========================================================
# KPI CARDS
# =========================================================

st.subheader("Key Performance Indicators")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Total Sales",
    f"${total_sales:,.0f}"
)

c2.metric(
    "Total Profit",
    f"${total_profit:,.0f}"
)

c3.metric(
    "Total Orders",
    f"{total_orders:,}"
)

c4.metric(
    "Profit Margin",
    f"{profit_margin:.2f}%"
)

c5.metric(
    "Customers",
    f"{total_customers:,}"
)

st.divider()


# =========================================================
# CHART CONFIGURATION
# =========================================================

CHART_TEMPLATE = "plotly_dark"

CHART_LAYOUT = {
    "template": CHART_TEMPLATE,
    "paper_bgcolor": "#111827",
    "plot_bgcolor": "#111827",
    "font": {"color": "#E2E8F0"},
    "margin": dict(l=30, r=30, t=50, b=30),
    "legend": dict(orientation="h", y=-0.25)
}


# =========================================================
# TAB LAYOUT
# =========================================================

tab1, tab2, tab3 = st.tabs([
    "📈 Overview",
    "🛍️ Products & Categories",
    "🚚 Operations & Discounts"
])


# =========================================================
# TAB 1: OVERVIEW
# =========================================================

with tab1:

    left, right = st.columns(2)

    # Monthly Sales Trend
    with left:
        st.subheader("Monthly Sales Trend")

        monthly = (
            filtered_df
            .set_index("order_date")
            .resample("MS")
            .agg(
                Sales=("sales", "sum"),
                Profit=("profit", "sum")
            )
            .reset_index()
        )

        fig = px.line(
            monthly,
            x="order_date",
            y=["Sales", "Profit"],
            markers=True,
            labels={
                "order_date": "Month",
                "value": "Amount ($)",
                "variable": "Metric"
            },
            color_discrete_sequence=["#22D3EE", "#34D399"]
        )

        fig.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    # Regional Performance
    with right:
        st.subheader("Regional Sales & Profit")

        regional = (
            filtered_df.groupby("region", as_index=False)
            .agg(
                Sales=("sales", "sum"),
                Profit=("profit", "sum")
            )
        )

        fig = px.bar(
            regional,
            x="region",
            y=["Sales", "Profit"],
            barmode="group",
            color_discrete_sequence=["#22D3EE", "#34D399"]
        )

        fig.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    # Customer Segment Analysis
    left, right = st.columns(2)

    with left:
        st.subheader("Sales by Customer Segment")

        segment_data = (
            filtered_df.groupby("segment", as_index=False)
            .agg(Sales=("sales", "sum"))
        )

        fig = px.pie(
            segment_data,
            names="segment",
            values="Sales",
            hole=0.55,
            color_discrete_sequence=[
                "#22D3EE", "#6366F1", "#34D399"
            ]
        )

        fig.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Sales Distribution")

        fig = px.histogram(
            filtered_df,
            x="sales",
            nbins=40,
            color_discrete_sequence=["#22D3EE"]
        )

        fig.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)


# =========================================================
# TAB 2: PRODUCTS & CATEGORIES
# =========================================================

with tab2:

    left, right = st.columns(2)

    with left:
        st.subheader("Sales by Category")

        category_sales = (
            filtered_df.groupby("category", as_index=False)
            .agg(Sales=("sales", "sum"))
            .sort_values("Sales", ascending=True)
        )

        fig = px.bar(
            category_sales,
            x="Sales",
            y="category",
            orientation="h",
            color="Sales",
            color_continuous_scale="Teal"
        )

        fig.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Profit by Category")

        category_profit = (
            filtered_df.groupby("category", as_index=False)
            .agg(Profit=("profit", "sum"))
            .sort_values("Profit", ascending=True)
        )

        fig = px.bar(
            category_profit,
            x="Profit",
            y="category",
            orientation="h",
            color="Profit",
            color_continuous_scale="Viridis"
        )

        fig.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 10 Products by Sales")

    top_products = (
        filtered_df.groupby("product_name", as_index=False)
        .agg(
            Sales=("sales", "sum"),
            Profit=("profit", "sum"),
            Quantity=("quantity", "sum")
        )
        .nlargest(10, "Sales")
        .sort_values("Sales", ascending=True)
    )

    fig = px.bar(
        top_products,
        x="Sales",
        y="product_name",
        orientation="h",
        hover_data=["Profit", "Quantity"],
        color="Sales",
        color_continuous_scale="Teal"
    )

    fig.update_layout(
        **CHART_LAYOUT,
        height=550
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Sub-Category Profitability")

    subcategory = (
        filtered_df.groupby("sub_category", as_index=False)
        .agg(Profit=("profit", "sum"))
        .sort_values("Profit", ascending=True)
    )

    fig = px.bar(
        subcategory,
        x="Profit",
        y="sub_category",
        orientation="h",
        color="Profit",
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0
    )

    fig.update_layout(**CHART_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)


# =========================================================
# TAB 3: OPERATIONS & DISCOUNTS
# =========================================================

with tab3:

    left, right = st.columns(2)

    with left:
        st.subheader("Shipping Duration by Mode")

        shipping = (
            filtered_df.groupby("ship_mode", as_index=False)
            .agg(
                Avg_Days=("shipping_duration", "mean"),
                Orders=("order_id", "nunique")
            )
        )

        fig = px.bar(
            shipping,
            x="ship_mode",
            y="Avg_Days",
            color="Avg_Days",
            color_continuous_scale="Teal",
            hover_data=["Orders"]
        )

        fig.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Discount vs Profit")

        fig = px.scatter(
            filtered_df,
            x="discount",
            y="profit",
            color="category",
            hover_data=["product_name", "sales"],
            opacity=0.65,
            color_discrete_sequence=[
                "#22D3EE", "#818CF8", "#34D399"
            ]
        )

        fig.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Average Profit by Discount Level")

    discount_data = filtered_df.copy()

    discount_data["discount_level"] = pd.cut(
        discount_data["discount"],
        bins=[-0.001, 0, 0.2, 0.4, 0.6, 1.0],
        labels=[
            "No Discount",
            "1–20%",
            "21–40%",
            "41–60%",
            "61–100%"
        ]
    )

    discount_summary = (
        discount_data.groupby(
            "discount_level",
            observed=False
        )
        .agg(
            Avg_Profit=("profit", "mean"),
            Orders=("order_id", "nunique")
        )
        .reset_index()
    )

    fig = px.bar(
        discount_summary,
        x="discount_level",
        y="Avg_Profit",
        color="Avg_Profit",
        color_continuous_scale="RdYlGn",
        hover_data=["Orders"]
    )

    fig.update_layout(**CHART_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)


# =========================================================
# DATA TABLE
# =========================================================

with st.expander("🔍 View Filtered Dataset"):

    st.write(
        f"Showing {len(filtered_df):,} records"
    )

    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=400
    )

    csv = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Filtered Data",
        data=csv,
        file_name="superstore_filtered_data.csv",
        mime="text/csv"
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Superstore Business Analytics | "
    "Built with Python, Streamlit & Plotly"
)
