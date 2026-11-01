import logging
import time

from etl.extract import extract_all
from etl.transform import transform_all
from etl.load import load_all


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pipeline.log")
    ]
)

logger = logging.getLogger(__name__)


# ============================================================
# DATA SOURCE
# ============================================================

CSV_PATH = "data/Sample - Superstore.csv"


# ============================================================
# PIPELINE
# ============================================================

def run_pipeline():

    start = time.time()

    logger.info("=" * 50)
    logger.info("Pipeline started")

    try:

        # ----------------------------------------------------
        # EXTRACT
        # ----------------------------------------------------

        logger.info("── Extract stage ──")

        raw = extract_all(
            CSV_PATH
        )

        # ----------------------------------------------------
        # TRANSFORM
        # ----------------------------------------------------

        transformed = transform_all(
            raw
        )

        # ----------------------------------------------------
        # LOAD
        # ----------------------------------------------------

        load_all(
            transformed
        )

        # ----------------------------------------------------
        # COMPLETE
        # ----------------------------------------------------

        elapsed = round(
            time.time() - start,
            2
        )

        logger.info(
            f"Pipeline finished in {elapsed}s ✓"
        )

        logger.info("=" * 50)

    except Exception as e:

        logger.error(
            f"Pipeline FAILED: {e}",
            exc_info=True
        )

        raise


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_pipeline()