import aiohttp
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class WebhookService:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def send_webhook(
        self, url: str, payload: dict, headers: dict | None = None, retries: int = 3
    ) -> bool:
        for attempt in range(retries):
            try:
                session = await self._get_session()

                webhook_headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "DataFlow-Webhook/1.0",
                }
                if headers:
                    webhook_headers.update(headers)

                async with session.post(
                    url,
                    json=payload,
                    headers=webhook_headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status < 400:
                        logger.info(f"Webhook sent successfully to {url}")
                        return True
                    else:
                        logger.warning(
                            f"Webhook failed with status {response.status}: {await response.text()}"
                        )

            except Exception as e:
                logger.error(f"Webhook attempt {attempt + 1} failed: {e}")

        logger.error(f"Webhook failed after {retries} attempts: {url}")
        return False

    async def send_pipeline_complete_webhook(
        self, webhook_url: str, job_id: str, result: dict
    ):
        payload = {
            "event": "pipeline.complete",
            "job_id": job_id,
            "status": "COMPLETE",
            "data": {
                "job_id": job_id,
                "dataset_id": result.get("dataset_id"),
                "file_path": result.get("file_path"),
                "total_tokens_used": result.get("total_tokens_used", 0),
                "total_cost_usd": result.get("total_cost_usd", 0),
                "insights_count": len(result.get("insights", [])),
                "charts_count": len(result.get("charts", [])),
                "has_report": bool(result.get("report_narrative")),
            },
        }

        return await self.send_webhook(webhook_url, payload)

    async def send_pipeline_failed_webhook(
        self, webhook_url: str, job_id: str, error: str
    ):
        payload = {
            "event": "pipeline.failed",
            "job_id": job_id,
            "status": "FAILED",
            "error": error,
        }

        return await self.send_webhook(webhook_url, payload)


webhook_service = WebhookService()


async def get_webhook() -> WebhookService:
    return webhook_service
