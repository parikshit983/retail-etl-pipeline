# scheduler.py
import schedule
import time
import logging
from pipeline import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def job():
    logger.info("Scheduled run triggered")
    run_pipeline()

# Run once immediately then every hour
job()
schedule.every(1).hours.do(job)

logger.info("Scheduler active -- press Ctrl+C to stop")
while True:
    schedule.run_pending()
    time.sleep(60)