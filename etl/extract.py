import pandas as pd
import logging

logger = logging.getLogger(__name__)


EXPECTED_COLUMNS = [
    "Row ID",
    "Order ID",
    "Order Date",
    "Ship Date",
    "Ship Mode",
    "Customer ID",
    "Customer Name",
    "Segment",
    "Country",
    "City",
    "State",
    "Postal Code",
    "Region",
    "Product ID",
    "Category",
    "Sub-Category",
    "Product Name",
    "Sales",
    "Quantity",
    "Discount",
    "Profit",
]


def extract_superstore(filepath: str) -> pd.DataFrame:

    logger.info(f"Extracting data from: {filepath}")

    df = pd.read_csv(
        filepath,
        encoding="latin-1",
        parse_dates=["Order Date", "Ship Date"],
        dayfirst=False,
    )

    logger.info(
        f"  -> Loaded {len(df):,} rows x {len(df.columns)} columns"
    )

    missing = set(EXPECTED_COLUMNS) - set(df.columns)

    if missing:
        logger.warning(f"  Missing columns: {missing}")
    else:
        logger.info("  All expected columns present ✓")

    return df


def extract_all(csv_path: str) -> dict:

    return {
        "superstore": extract_superstore(csv_path)
    }