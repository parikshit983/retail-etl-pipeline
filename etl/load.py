import logging
import pandas as pd

from sqlalchemy import create_engine

logger = logging.getLogger(__name__)


# ============================================================
# SQLITE DATABASE
# ============================================================

DATABASE_URL = "sqlite:///retail.db"


def get_engine():

    engine = create_engine(
        DATABASE_URL,
        echo=False
    )

    logger.info(
        "  SQLite database engine created ✓"
    )

    return engine


# ============================================================
# LOAD DATAFRAME
# ============================================================

def load_dataframe(
    df: pd.DataFrame,
    table: str,
    engine
):

    df = df.copy()

    # Convert column names to database-friendly names
    df.columns = [
        column
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        for column in df.columns
    ]

    # Convert datetime columns
    for column in df.columns:

        if pd.api.types.is_datetime64_any_dtype(
            df[column]
        ):
            df[column] = (
                df[column]
                .dt.strftime("%Y-%m-%d")
            )

    # Convert categorical columns
    for column in df.columns:

        if str(df[column].dtype) == "category":

            df[column] = (
                df[column]
                .astype(str)
            )

    # Replace NaN with None
    df = df.where(
        pd.notnull(df),
        None
    )

    # Write to SQLite
    df.to_sql(
        table,
        engine,
        if_exists="replace",
        index=False
    )

    logger.info(
        f"  Loaded {len(df):,} rows -> '{table}' ✓"
    )


# ============================================================
# COMPLETE LOAD
# ============================================================

def load_all(transformed: dict):

    logger.info(
        "── Load stage started ──"
    )

    # Create SQLite engine
    engine = get_engine()

    # Load cleaned data
    load_dataframe(
        transformed["sales_clean"],
        "sales_clean",
        engine
    )

    # Load monthly summary
    load_dataframe(
        transformed["monthly_sales_summary"],
        "monthly_sales_summary",
        engine
    )

    # Load region summary
    load_dataframe(
        transformed["region_performance"],
        "region_performance",
        engine
    )

    # Load product summary
    load_dataframe(
        transformed["product_performance"],
        "product_performance",
        engine
    )

    logger.info(
        "── Load stage complete ✓ ──"
    )