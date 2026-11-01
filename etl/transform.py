import pandas as pd
import logging

logger = logging.getLogger(__name__)


def handle_nulls(df: pd.DataFrame) -> pd.DataFrame:

    before = df.isnull().sum().sum()

    df["Postal Code"] = (
        df["Postal Code"]
        .fillna(0)
        .astype(int)
    )

    df["Customer Name"] = (
        df["Customer Name"]
        .fillna("Unknown")
    )

    df["Product Name"] = (
        df["Product Name"]
        .fillna("Unknown Product")
    )

    df = df.dropna(
        subset=[
            "Order ID",
            "Sales",
            "Order Date"
        ]
    )

    after = df.isnull().sum().sum()

    logger.info(
        f"  Nulls: {before} -> {after} remaining"
    )

    return df


def cast_types(df: pd.DataFrame) -> pd.DataFrame:

    df["Order Date"] = pd.to_datetime(
        df["Order Date"]
    )

    df["Ship Date"] = pd.to_datetime(
        df["Ship Date"]
    )

    df["Sales"] = (
        df["Sales"]
        .astype(float)
        .round(2)
    )

    df["Profit"] = (
        df["Profit"]
        .astype(float)
        .round(2)
    )

    df["Quantity"] = (
        df["Quantity"]
        .astype(int)
    )

    df["Discount"] = (
        df["Discount"]
        .astype(float)
        .round(2)
    )

    df["Row ID"] = (
        df["Row ID"]
        .astype(int)
    )

    logger.info("  Type casting complete ✓")

    return df


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:

    df["order_year"] = (
        df["Order Date"].dt.year
    )

    df["order_month"] = (
        df["Order Date"]
        .dt.to_period("M")
        .astype(str)
    )

    df["order_quarter"] = (
        df["Order Date"]
        .dt.quarter
        .map(lambda q: f"Q{q}")
    )

    df["ship_days"] = (
        df["Ship Date"] -
        df["Order Date"]
    ).dt.days

    df["profit_margin"] = (
        (
            df["Profit"] /
            df["Sales"].replace(
                0,
                float("nan")
            )
        ) * 100
    ).round(2)

    df["discount_tier"] = pd.cut(
        df["Discount"],
        bins=[
            -0.01,
            0.0,
            0.1,
            0.2,
            0.3,
            1.0
        ],
        labels=[
            "No Discount",
            "Low",
            "Medium",
            "High",
            "Very High"
        ]
    ).astype(str)

    df["is_profitable"] = (
        df["Profit"] > 0
    )

    logger.info(
        "  Derived columns added ✓"
    )

    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:

    before = len(df)

    df = df.drop_duplicates(
        subset=["Row ID"]
    )

    after = len(df)

    logger.info(
        f"  Duplicates removed: {before - after}"
    )

    return df


def agg_monthly_sales(
    df: pd.DataFrame
) -> pd.DataFrame:

    result = (
        df.groupby(
            [
                "order_month",
                "order_year",
                "Category"
            ]
        )
        .agg(
            total_sales=("Sales", "sum"),
            total_profit=("Profit", "sum"),
            total_orders=("Order ID", "nunique"),
            total_units=("Quantity", "sum"),
            avg_discount=("Discount", "mean"),
        )
        .reset_index()
    )

    result["total_sales"] = (
        result["total_sales"].round(2)
    )

    result["total_profit"] = (
        result["total_profit"].round(2)
    )

    result["avg_discount"] = (
        result["avg_discount"].round(3)
    )

    logger.info(
        f"  monthly_sales_summary -> {len(result):,} rows"
    )

    return result


def agg_region_performance(
    df: pd.DataFrame
) -> pd.DataFrame:

    result = (
        df.groupby(
            [
                "Region",
                "Segment"
            ]
        )
        .agg(
            total_sales=("Sales", "sum"),
            total_profit=("Profit", "sum"),
            total_orders=("Order ID", "nunique"),
            avg_ship_days=("ship_days", "mean"),
        )
        .reset_index()
    )

    result["total_sales"] = (
        result["total_sales"].round(2)
    )

    result["total_profit"] = (
        result["total_profit"].round(2)
    )

    result["avg_ship_days"] = (
        result["avg_ship_days"].round(1)
    )

    logger.info(
        f"  region_performance -> {len(result):,} rows"
    )

    return result


def agg_product_performance(
    df: pd.DataFrame
) -> pd.DataFrame:

    result = (
        df.groupby(
            [
                "Product ID",
                "Product Name",
                "Category",
                "Sub-Category"
            ]
        )
        .agg(
            total_sales=("Sales", "sum"),
            total_profit=("Profit", "sum"),
            total_units=("Quantity", "sum"),
            avg_margin=("profit_margin", "mean"),
            total_orders=("Order ID", "nunique"),
        )
        .reset_index()
    )

    result["total_sales"] = (
        result["total_sales"].round(2)
    )

    result["total_profit"] = (
        result["total_profit"].round(2)
    )

    result["avg_margin"] = (
        result["avg_margin"].round(2)
    )

    logger.info(
        f"  product_performance -> {len(result):,} rows"
    )

    return result


def transform_all(raw: dict) -> dict:

    logger.info(
        "── Transform stage started ──"
    )

    df = raw["superstore"]

    df = remove_duplicates(df)

    df = handle_nulls(df)

    df = cast_types(df)

    df = add_derived_columns(df)

    return {
        "sales_clean": df,

        "monthly_sales_summary":
            agg_monthly_sales(df),

        "region_performance":
            agg_region_performance(df),

        "product_performance":
            agg_product_performance(df),
    }