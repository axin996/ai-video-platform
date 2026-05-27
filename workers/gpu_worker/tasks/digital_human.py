"""Step 5: Generate digital human talking video via HeyGem."""

import os
import time

import httpx

from ..app import celery_app
from ...core.config import settings


@celery_app.task(bind=True, name="pipeline.digital_human", queue="pipeline_queue",
                  acks_late=True, soft_time_limit=3600, time_limit=3900)
def generate_digital_human(self, task_id: str, audio_path: str, pipeline_params: dict) -> dict:
    """
    Generate digital human video synced to TTS audio using HeyGem.
    HeyGem produces lip-synced talking-head video from audio input.
    Returns: {video_path, duration_seconds}
    """
    dh_config = pipeline_params.get("digital_human", {})
    model_id = dh_config.get("model_id", "default")
    background = dh_config.get("background_color", "#FFFFFF")
    position = dh_config.get("position", "center")

    task_dir = os.path.join(settings.TEMP_DIR, task_id, "video")
    os.makedirs(task_dir, exist_ok=True)
    output_path = os.path.join(task_dir, "digital_human_raw.mp4")

    payload = {
        "audio_url": audio_path,
        "model_id": model_id,
        "background": background,
        "position": position,
    }

    max_retries = 2
    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=3600) as client:
                response = client.post(
                    f"{settings.HEYGEM_BASE_URL}/api/v1/video/generate",
                    json=payload,
                )
                response.raise_for_status()

                with open(output_path, "wb") as f:
                    f.write(response.content)

                break
        except Exception as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"HeyGem generation failed after {max_retries} attempts: {e}")
            time.sleep(5)

    # Get video duration
    import subprocess
    duration = 0.0
    try:
        result = subprocess.run([
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            output_path,
        ], capture_output=True, text=True)
        duration = float(result.stdout.strip())
    except Exception:
        pass

    return {
        "video_path": output_path,
        "duration_seconds": duration,
    }
