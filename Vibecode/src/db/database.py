import os
import json
import logging
import math
import threading
from typing import Any, Optional
from datetime import datetime
from src.config import get_settings

logger = logging.getLogger(__name__)


class _SafeEncoder(json.JSONEncoder):
    """JSON encoder that handles numpy scalars, pandas NA, and other non-serializable types."""
    def default(self, obj):
        try:
            import numpy as np
            if isinstance(obj, (np.integer,)):
                return int(obj)
            if isinstance(obj, (np.floating,)):
                v = float(obj)
                return None if (math.isnan(v) or math.isinf(v)) else v
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, np.bool_):
                return bool(obj)
        except ImportError:
            pass
        try:
            import pandas as pd
            if pd.isna(obj):
                return None
        except (ImportError, TypeError, ValueError):
            pass
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)


def _safe_json_dumps(obj) -> str:
    """Serialize obj to JSON string, safely handling numpy/pandas types."""
    return json.dumps(obj, cls=_SafeEncoder)


class JobStore:
    """In-memory job storage."""

    def __init__(self):
        self._lock = threading.Lock()
        self._jobs = {}
        self._stages = {}

    def create_job(
        self, job_id: str, dataset_id: str, file_path: str, user_config: dict
    ) -> dict:
        with self._lock:
            self._jobs[job_id] = {
                "job_id": job_id,
                "dataset_id": dataset_id,
                "file_path": file_path,
                "user_config": _safe_json_dumps(user_config)
                if isinstance(user_config, dict)
                else user_config,
                "status": "PENDING",
                "total_tokens_used": 0,
                "total_cost_usd": 0.0,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
            return self._jobs[job_id]

    def update_job(self, job_id: str, **kwargs):
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].update(kwargs)
                self._jobs[job_id]["updated_at"] = datetime.utcnow().isoformat()

    def get_job(self, job_id: str) -> Optional[dict]:
        with self._lock:
            return self._jobs.get(job_id)

    def get_all_jobs(self) -> list:
        with self._lock:
            return list(self._jobs.values())

    def create_stage(
        self, job_id: str, stage_name: str, status: str = "PENDING", output: dict = None
    ):
        with self._lock:
            key = f"{job_id}:{stage_name}"
            self._stages[key] = {
                "job_id": job_id,
                "stage_name": stage_name,
                "status": status,
                "output": _safe_json_dumps(output) if output else None,
                "started_at": datetime.utcnow().isoformat(),
                "completed_at": None,
            }

    def update_stage(
        self, job_id: str, stage_name: str, status: str, output: dict = None
    ):
        with self._lock:
            key = f"{job_id}:{stage_name}"
            if key in self._stages:
                self._stages[key]["status"] = status
                if output:
                    try:
                        self._stages[key]["output"] = _safe_json_dumps(output)
                    except Exception as e:
                        logger.error(f"[JobStore] Failed to serialize stage {stage_name}: {e}")
                        self._stages[key]["output"] = json.dumps({"error": "serialization_failed"})
                if status == "COMPLETE":
                    self._stages[key]["completed_at"] = datetime.utcnow().isoformat()
            else:
                try:
                    serialized = _safe_json_dumps(output) if output else None
                except Exception:
                    serialized = json.dumps({"error": "serialization_failed"})
                self._stages[key] = {
                    "job_id": job_id,
                    "stage_name": stage_name,
                    "status": status,
                    "output": serialized,
                    "started_at": datetime.utcnow().isoformat(),
                    "completed_at": datetime.utcnow().isoformat()
                    if status == "COMPLETE"
                    else None,
                }

    def get_stages(self, job_id: str) -> list:
        with self._lock:
            return [s for k, s in self._stages.items() if s["job_id"] == job_id]


job_store = JobStore()


class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        logger.info("Using in-memory storage only")
        self.pool = None

    async def disconnect(self):
        pass

    async def execute(self, query: str, *args) -> list:
        return []

    async def execute_one(self, query: str, *args) -> Optional[dict]:
        return None


db = Database()


async def get_db() -> Database:
    return db


async def create_tables(db: Database):
    logger.info("Tables not needed - using in-memory store")
