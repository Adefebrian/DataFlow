import asyncio
import logging
import sys
import os
import time

sys.path.insert(0, "/app")

from src.db.database import job_store
from src.services.pipeline import run_pipeline
from src.services.redis import get_redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Worker started - monitoring in-memory job store")
    logger.info("Note: Pipeline is now run directly by API")

    while True:
        try:
            await asyncio.sleep(10)
        except Exception as e:
            logger.error(f"Worker error: {e}")
            await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
