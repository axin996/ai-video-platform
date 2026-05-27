"""Celery application for GPU-intensive pipeline tasks."""

import sys
from pathlib import Path

# Ensure project root and backend are in Python path
_PROJ_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJ_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJ_ROOT))
if str(_PROJ_ROOT / "backend") not in sys.path:
    sys.path.insert(0, str(_PROJ_ROOT / "backend"))

from celery import Celery
from celery.signals import worker_ready, worker_shutdown

from ..core.config import settings

celery_app = Celery(
    "ai_video_gpu_worker",
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
    task_default_queue="pipeline_queue",
    task_routes={
        "pipeline.orchestrator": {"queue": "pipeline_queue"},
        "pipeline.download": {"queue": "pipeline_queue"},
        "pipeline.extract": {"queue": "pipeline_queue"},
        "pipeline.rewrite": {"queue": "pipeline_queue"},
        "pipeline.tts": {"queue": "pipeline_queue"},
        "pipeline.digital_human": {"queue": "pipeline_queue"},
        "pipeline.composite": {"queue": "pipeline_queue"},
    },
    worker_concurrency=1,
    worker_prefetch_multiplier=1,
    result_expires=86400,
)

# Preloaded models (loaded once at worker startup)
whisper_model = None
heygem_models = None


@worker_ready.connect
def on_worker_ready(**kwargs):
    """Preload AI models when worker starts to avoid cold-start latency."""
    global whisper_model, heygem_models
    try:
        from faster_whisper import WhisperModel
        whisper_model = WhisperModel(
            settings.WHISPER_MODEL_SIZE,
            device=settings.WHISPER_DEVICE,
            compute_type=settings.WHISPER_COMPUTE_TYPE,
        )
        print(f"[GPU Worker] Whisper model '{settings.WHISPER_MODEL_SIZE}' loaded successfully")
    except Exception as e:
        print(f"[GPU Worker] Warning: Whisper model not loaded: {e}")
        whisper_model = None

    try:
        # HeyGem model loading placeholder
        # heygem_models = load_heygem_models(settings.HEYGEM_MODELS_DIR)
        pass
    except Exception as e:
        print(f"[GPU Worker] Warning: HeyGem models not loaded: {e}")
        heygem_models = None


@worker_shutdown.connect
def on_worker_shutdown(**kwargs):
    """Clean up resources on worker shutdown."""
    global whisper_model, heygem_models
    whisper_model = None
    heygem_models = None
