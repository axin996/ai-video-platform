"""Celery application for platform upload workers."""

import sys
from pathlib import Path

# Ensure project root and backend are in Python path
_PROJ_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJ_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJ_ROOT))
if str(_PROJ_ROOT / "backend") not in sys.path:
    sys.path.insert(0, str(_PROJ_ROOT / "backend"))

from celery import Celery

from ..core.config import settings

celery_app = Celery(
    "ai_video_upload_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_queue="upload_queue",
    task_routes={
        "pipeline.publish": {"queue": "upload_queue"},
        "pipeline.publish.douyin": {"queue": "upload_queue"},
        "pipeline.publish.xhs": {"queue": "upload_queue"},
        "pipeline.publish.shipinhao": {"queue": "upload_queue"},
        "pipeline.publish.bilibili": {"queue": "upload_queue"},
        "pipeline.publish.youtube": {"queue": "upload_queue"},
    },
    worker_concurrency=2,
    worker_prefetch_multiplier=1,
)
