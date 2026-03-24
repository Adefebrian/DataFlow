import json
import hashlib
from datetime import datetime
from src.db.database import Database
from src.models.types import PipelineState, PipelineStage
from typing import Literal


class CheckpointManager:
    def __init__(self, db: Database):
        self.db = db

    def compute_hash(self, state: PipelineState) -> str:
        state_dict = state.model_dump(mode="json")
        canonical = json.dumps(state_dict, sort_keys=True, default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    async def save(
        self,
        state: PipelineState,
        stage_name: str,
    ):
        state.last_checkpoint = datetime.utcnow().isoformat()
        state.checkpoint_hash = self.compute_hash(state)

        await self.upsert_pipeline_stage(
            job_id=state.job_id,
            stage_name=stage_name,
            status="COMPLETE",
            output=state.model_dump(mode="json"),
        )

    async def upsert_pipeline_stage(
        self,
        job_id: str,
        stage_name: str,
        status: Literal["PENDING", "RUNNING", "COMPLETE", "FAILED"],
        output: dict | None = None,
    ) -> PipelineStage:
        result = await self.db.execute_one(
            """
            INSERT INTO pipeline_stages (id, job_id, stage_name, status, output, started_at)
            VALUES (gen_random_uuid(), $1, $2, $3, $4, NOW())
            ON CONFLICT (job_id, stage_name)
            DO UPDATE SET
                status = EXCLUDED.status,
                output = COALESCE(EXCLUDED.output, pipeline_stages.output),
                completed_at = CASE
                    WHEN EXCLUDED.status IN ('COMPLETE', 'FAILED') THEN NOW()
                    ELSE pipeline_stages.completed_at
                END
            RETURNING *
            """,
            job_id,
            stage_name,
            status,
            json.dumps(output) if output else None,
        )
        return PipelineStage(**result) if result else None

    async def load_checkpoint(self, job_id: str, stage_name: str) -> dict | None:
        result = await self.db.execute_one(
            """
            SELECT output FROM pipeline_stages
            WHERE job_id = $1 AND stage_name = $2 AND status = 'COMPLETE'
            """,
            job_id,
            stage_name,
        )
        return result["output"] if result else None

    async def get_latest_stage(self, job_id: str) -> PipelineStage | None:
        result = await self.db.execute_one(
            """
            SELECT * FROM pipeline_stages
            WHERE job_id = $1
            ORDER BY completed_at DESC NULLS LAST
            LIMIT 1
            """,
            job_id,
        )
        return PipelineStage(**result) if result else None
