# dashboard.py

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Retail Sales Dashboard",
    page_icon="🛒",
    layout="wide"
)


# ============================================================
# SQLITE DATABASE
# ============================================================

DATABASE_URL = "sqlite:///retail.db"


@st.cache_resource
def get_engine():

    return create_engine(
        DATABASE_URL,
        echo=False
    )


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    engine = get_engine()

    sales = pd.read_sql(
        "SELECT * FROM sales_clean",
        engine
    )

    monthly = pd.read_sql(
        "SELECT * FROM monthly_sales_summary",
        engine
    )

    region = pd.read_sql(
        "SELECT * FROM region_performance",
        engine
    )

    product = pd.read_sql(
        "SELECT * FROM product_performance",
        engine
    )

    return sales, monthly, region, product


# ============================================================
# CHECK DATABASE
# ============================================================

try:

    with st.spinner("Loading data from SQLite..."):

        sales, monthly, region, product = load_data()

except Exception as e:

    st.error("Unable to load the SQLite database.")

    st.error(str(e))

    st.info(
        "Make sure you run 'python pipeline.py' first "
        "so that retail.db is created."
    )

    st.stop()


# ============================================================
# TITLE
# ============================================================

st.title("🛒 Retail Sales ETL Dashboard")

st.caption(
    "Data sourced from Kaggle Superstore Dataset "
    "via ETL Pipeline and SQLite"
)

st.divider()


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("Key Metrics")

col1, col2, col3, col4 = st.columns(4)


with col1:

    total_sales = sales["sales"].sum()

    st.metric(
        "Total Sales",
        f"${total_sales:,.0f}"
    )


with col2:

    total_profit = sales["profit"].sum()

    st.metric(
        "Total Profit",
        f"${total_profit:,.0f}"
    )


with col3:

    total_orders = sales["order_id"].nunique()

    st.metric(
        "Total Orders",
        f"{total_orders:,}"
    )


with col4:

    avg_margin = sales["profit_margin"].mean()

    st.metric(
        "Avg Profit Margin",
        f"{avg_margin:.1f}%"
    )


st.divider()


# ============================================================
# ROW 1
# SALES TREND + CATEGORY BREAKDOWN
# ============================================================

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# MONTHLY SALES TREND
# ------------------------------------------------------------

with col1:

    st.subheader("Monthly Sales Trend")

    trend = (
        monthly
        .groupby("order_month")["total_sales"]
        .sum()
        .reset_index()
        .sort_values("order_month")
    )

    fig = px.line(
        trend,
        x="order_month",
        y="total_sales",
        markers=True,
        labels={
            "order_month": "Month",
            "total_sales": "Total Sales ($)"
        }
    )

    fig.update_layout(
        xaxis_tickangle=-45
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ------------------------------------------------------------
# SALES BY CATEGORY
# ------------------------------------------------------------

with col2:

    st.subheader("Sales by Category")

    cat = (
        monthly
        .groupby("category")["total_sales"]
        .sum()
        .reset_index()
    )

    fig2 = px.pie(
        cat,
        values="total_sales",
        names="category",
        hole=0.4
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


st.divider()


# ============================================================
# ROW 2
# REGION PERFORMANCE + PROFIT BY CATEGORY
# ============================================================

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# REGION PERFORMANCE
# ------------------------------------------------------------

with col1:

    st.subheader("Region Performance")

    fig3 = px.bar(
        region.sort_values(
            "total_sales",
            ascending=True
        ),
        x="total_sales",
        y="region",
        color="segment",
        orientation="h",
        labels={
            "total_sales": "Total Sales ($)",
            "region": "Region"
        },
        barmode="group"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )


# ------------------------------------------------------------
# PROFIT BY CATEGORY
# ------------------------------------------------------------

with col2:

    st.subheader("Profit by Category")

    cat_profit = (
        monthly
        .groupby("category")["total_profit"]
        .sum()
        .reset_index()
    )

    fig4 = px.bar(
        cat_profit.sort_values(
            "total_profit",
            ascending=False
        ),
        x="category",
        y="total_profit",
        color="category",
        labels={
            "total_profit": "Total Profit ($)",
            "category": "Category"
        }
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )


st.divider()


# ============================================================
# ROW 3
# TOP PRODUCTS + LOSS MAKING PRODUCTS
# ============================================================

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# TOP 10 PRODUCTS
# ------------------------------------------------------------

with col1:

    st.subheader("Top 10 Products by Profit")

    top10 = (
        product
        .nlargest(10, "total_profit")
        [
            [
                "product_name",
                "category",
                "total_profit"
            ]
        ]
    )

    fig5 = px.bar(
        top10.sort_values(
            "total_profit"
        ),
        x="total_profit",
        y="product_name",
        color="category",
        orientation="h",
        labels={
            "total_profit": "Total Profit ($)",
            "product_name": "Product"
        }
    )

    st.plotly_chart(
        fig5,
        use_container_width=True
    )


# ------------------------------------------------------------
# LOSS MAKING PRODUCTS
# ------------------------------------------------------------

with col2:

    st.subheader("Top 10 Loss Making Products")

    bottom10 = (
        product
        .nsmallest(10, "total_profit")
        [
            [
                "product_name",
                "category",
                "total_profit"
            ]
        ]
    )

    fig6 = px.bar(
        bottom10.sort_values(
            "total_profit",
            ascending=False
        ),
        x="total_profit",
        y="product_name",
        color="category",
        orientation="h",
        labels={
            "total_profit": "Total Profit ($)",
            "product_name": "Product"
        }
    )

    st.plotly_chart(
        fig6,
        use_container_width=True
    )


st.divider()


# ============================================================
# ROW 4
# DISCOUNT + SHIPPING
# ============================================================

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# SALES BY DISCOUNT TIER
# ------------------------------------------------------------

with col1:

    st.subheader("Sales by Discount Tier")

    disc = (
        sales
        .groupby("discount_tier")["sales"]
        .sum()
        .reset_index()
    )

    fig7 = px.bar(
        disc.sort_values(
            "sales",
            ascending=False
        ),
        x="discount_tier",
        y="sales",
        color="discount_tier",
        labels={
            "sales": "Total Sales ($)",
            "discount_tier": "Discount Tier"
        }
    )

    st.plotly_chart(
        fig7,
        use_container_width=True
    )


# ------------------------------------------------------------
# SHIPPING DAYS
# ------------------------------------------------------------

with col2:

    st.subheader(
        "Avg Shipping Days by Region & Segment"
    )

    fig8 = px.bar(
        region.sort_values(
            "avg_ship_days",
            ascending=False
        ),
        x="region",
        y="avg_ship_days",
        color="segment",
        barmode="group",
        labels={
            "avg_ship_days": "Avg Ship Days",
            "region": "Region"
        }
    )

    st.plotly_chart(
        fig8,
        use_container_width=True
    )


st.divider()


# ============================================================
# RAW DATA
# ============================================================

st.subheader("Raw Sales Data")

st.dataframe(
    sales[
        [
            "order_id",
            "order_date",
            "customer_name",
            "category",
            "region",
            "sales",
            "profit",
            "profit_margin",
            "discount_tier",
            "ship_days"
        ]
    ].head(100),
    use_container_width=True
)

st.caption(
    "Showing first 100 rows of cleaned sales data"
)