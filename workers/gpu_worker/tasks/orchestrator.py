"""Pipeline orchestrator: chains all 6 steps sequentially with error handling.

State machine:
  pending → downloading → extracting → rewriting → tts_synthesizing
                                                          ↓
  completed ← publishing ← compositing ← digital_human ←─┘
      ↑           ↑             ↑             ↑
      └───────────┴─────────────┴── failed ←──┘
"""

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

from celery import group
from loguru import logger

# Ensure project root is in path for backend imports
_PROJ_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJ_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJ_ROOT))
if str(_PROJ_ROOT / "backend") not in sys.path:
    sys.path.insert(0, str(_PROJ_ROOT / "backend"))

from ..app import celery_app
from .download import download_video
from .extract import extract_script
from .rewrite import rewrite_script
from .tts import synthesize_tts
from .digital_human import generate_digital_human
from .composite import composite_video


def _run_async(coro):
    """Run an async coroutine in a way that works on Windows."""
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _get_db_engine():
    from sqlalchemy.ext.asyncio import create_async_engine
    from ...core.config import settings
    return create_async_engine(settings.DATABASE_URL)


def _update_task_status(task_id: str, status: str, error_message: str | None = None):
    """Update task status in the database."""
    try:
        from sqlalchemy import select
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.models import Task

        engine = _get_db_engine()

        async def _update():
            async with AsyncSession(engine) as session:
                result = await session.execute(select(Task).where(Task.id == task_id))
                task = result.scalar_one_or_none()
                if task:
                    task.status = status
                    if error_message:
                        task.error_message = error_message
                    await session.commit()

        _run_async(_update())
    except Exception as e:
        logger.warning(f"Could not update task status in DB: {e}")


def _update_step_status(task_id: str, step_name: str, status: str,
                         output_result: dict | None = None, error_message: str | None = None):
    """Update step status in the database."""
    try:
        from sqlalchemy import select
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.models import TaskStep

        engine = _get_db_engine()

        async def _update():
            async with AsyncSession(engine) as session:
                result = await session.execute(
                    select(TaskStep).where(
                        TaskStep.task_id == task_id,
                        TaskStep.step_name == step_name,
                    )
                )
                step = result.scalar_one_or_none()
                if not step:
                    step = TaskStep(task_id=task_id, step_name=step_name)
                    session.add(step)

                step.status = status
                if status == "running" and not step.started_at:
                    step.started_at = datetime.now(timezone.utc)
                if status == "completed":
                    step.completed_at = datetime.now(timezone.utc)
                    if step.started_at:
                        step.duration_ms = int(
                            (step.completed_at - step.started_at).total_seconds() * 1000
                        )
                    if output_result:
                        step.output_result = output_result
                if status == "failed":
                    step.error_message = error_message

                await session.commit()

        _run_async(_update())
    except Exception as e:
        logger.warning(f"Could not update step status in DB: {e}")


def _fetch_task(task_id: str):
    """Fetch task from database."""
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.models import Task

    engine = _get_db_engine()

    async def _fetch():
        async with AsyncSession(engine) as session:
            result = await session.execute(select(Task).where(Task.id == task_id))
            return result.scalar_one_or_none()

    return _run_async(_fetch())


@celery_app.task(bind=True, name="pipeline.orchestrator", queue="pipeline_queue",
                  acks_late=True, reject_on_worker_lost=True,
                  max_retries=3, default_retry_delay=60, track_started=True)
def run_pipeline(self, task_id: str):
    """
    Master orchestrator. Runs the full 7-step pipeline sequentially.
    Each step's result is passed to the next step.
    On failure, saves context to DB and retries from the failed step.
    """
    logger.info(f"Pipeline started for task: {task_id}")

    task = _fetch_task(task_id)
    if not task:
        logger.error(f"Task not found: {task_id}")
        return {"error": "Task not found"}

    pipeline_params = task.pipeline_params or {}
    source_url = task.source_video_url
    video_path = None
    script_text = None
    rewritten_text = None
    srt_path = None
    audio_path = None
    dh_video_path = None

    try:
        # ── Step 1: Download ──
        _update_task_status(task_id, "downloading")
        _update_step_status(task_id, "download", "running")
        download_result = download_video.delay(task_id, source_url).get(timeout=600)
        video_path = download_result["video_path"]
        _update_step_status(task_id, "download", "completed", output_result=download_result)
        logger.info(f"Task {task_id}: Download complete -> {video_path}")

        # ── Step 2: Extract (Whisper) ──
        _update_task_status(task_id, "extracting")
        _update_step_status(task_id, "extract", "running")
        extract_result = extract_script.delay(task_id, video_path).get(timeout=900)
        script_text = extract_result["script_text"]
        srt_path = extract_result.get("srt_path")
        _update_step_status(task_id, "extract", "completed", output_result=extract_result)
        logger.info(f"Task {task_id}: Extract complete ({len(script_text)} chars)")

        # ── Step 3: Rewrite (DeepSeek) ──
        if pipeline_params.get("script_rewrite", {}).get("enabled", True) and script_text:
            _update_task_status(task_id, "rewriting")
            _update_step_status(task_id, "rewrite", "running")
            rewrite_result = rewrite_script.delay(task_id, script_text, pipeline_params).get(timeout=300)
            rewritten_text = rewrite_result["rewritten_text"]
            _update_step_status(task_id, "rewrite", "completed", output_result=rewrite_result)
            logger.info(f"Task {task_id}: Rewrite complete ({len(rewritten_text)} chars)")
        else:
            rewritten_text = script_text
            _update_step_status(task_id, "rewrite", "skipped")

        # ── Step 4: TTS (CosyVoice) ──
        text_for_tts = rewritten_text or script_text
        if pipeline_params.get("voice_clone", {}).get("enabled", True) and text_for_tts:
            _update_task_status(task_id, "tts_synthesizing")
            _update_step_status(task_id, "tts", "running")
            tts_result = synthesize_tts.delay(task_id, text_for_tts, pipeline_params).get(timeout=600)
            audio_path = tts_result["audio_path"]
            _update_step_status(task_id, "tts", "completed", output_result=tts_result)
            logger.info(f"Task {task_id}: TTS complete -> {audio_path}")
        else:
            audio_path = extract_result.get("audio_path")
            _update_step_status(task_id, "tts", "skipped")

        # ── Step 5: Digital Human (HeyGem) ──
        if pipeline_params.get("digital_human", {}).get("enabled", True) and audio_path:
            _update_task_status(task_id, "digital_human")
            _update_step_status(task_id, "digital_human", "running")
            dh_result = generate_digital_human.delay(task_id, audio_path, pipeline_params).get(timeout=1800)
            dh_video_path = dh_result["video_path"]
            _update_step_status(task_id, "digital_human", "completed", output_result=dh_result)
            logger.info(f"Task {task_id}: Digital human complete -> {dh_video_path}")
        else:
            _update_step_status(task_id, "digital_human", "skipped")

        # ── Step 6: Composite (FFmpeg) ──
        _update_task_status(task_id, "compositing")
        _update_step_status(task_id, "composite", "running")
        composite_result = composite_video.delay(
            task_id,
            dh_video_path or video_path,
            srt_path,
            pipeline_params,
        ).get(timeout=600)
        output_path = composite_result["video_path"]
        _update_step_status(task_id, "composite", "completed", output_result=composite_result)
        logger.info(f"Task {task_id}: Composite complete -> {output_path}")

        # ── Step 7: Publish (Multi-platform) ──
        targets = task.publish_targets or []
        if targets:
            _update_task_status(task_id, "publishing")
            _update_step_status(task_id, "publish", "running")
            from workers.upload_worker.tasks.publish import publish_to_platform
            publish_jobs = [
                publish_to_platform.s(task_id, output_path, platform, pipeline_params)
                for platform in targets
            ]
            job_group = group(publish_jobs)
            publish_results = job_group().get(timeout=1800)
            _update_step_status(task_id, "publish", "completed",
                                output_result={"platforms": publish_results})
            logger.info(f"Task {task_id}: Publish complete")

        # ── Done ──
        _update_task_status(task_id, "completed")
        logger.info(f"Task {task_id}: Pipeline completed successfully")
        return {"status": "completed", "task_id": task_id, "output_path": output_path}

    except Exception as exc:
        logger.error(f"Task {task_id}: Pipeline failed: {exc}")
        _update_task_status(task_id, "failed", error_message=str(exc))
        raise self.retry(exc=exc)
