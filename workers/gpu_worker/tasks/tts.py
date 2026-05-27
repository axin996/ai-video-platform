"""Step 4: Voice cloning and TTS synthesis via CosyVoice."""

import os
import time

import httpx

from ..app import celery_app
from ...core.config import settings


@celery_app.task(bind=True, name="pipeline.tts", queue="pipeline_queue",
                  acks_late=True, soft_time_limit=600, time_limit=900)
def synthesize_tts(self, task_id: str, rewritten_text: str, pipeline_params: dict) -> dict:
    """
    Synthesize speech with cloned voice via CosyVoice HTTP API.
    CosyVoice runs as a standalone service on port 9880.
    Returns: {audio_path, duration_seconds}
    """
    voice_config = pipeline_params.get("voice_clone", {})
    speed = voice_config.get("speed", 1.0)
    emotion = voice_config.get("emotion", "neutral")
    reference_audio_url = voice_config.get("reference_audio_url")

    task_dir = os.path.join(settings.TEMP_DIR, task_id, "audio")
    os.makedirs(task_dir, exist_ok=True)
    output_path = os.path.join(task_dir, "tts_output.wav")

    payload = {
        "text": rewritten_text,
        "speaker": "clone" if reference_audio_url else "default",
        "speed": speed,
        "emotion": emotion,
    }

    if reference_audio_url:
        # Download reference audio if provided
        import requests
        ref_path = os.path.join(task_dir, "reference_audio.wav")
        resp = requests.get(reference_audio_url, timeout=60)
        resp.raise_for_status()
        with open(ref_path, "wb") as f:
            f.write(resp.content)
        payload["prompt_speech"] = ref_path

    # Call CosyVoice API
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=600) as client:
                response = client.post(
                    f"{settings.COSYVOICE_BASE_URL}/",
                    json=payload,
                )
                response.raise_for_status()

                with open(output_path, "wb") as f:
                    f.write(response.content)

                break
        except Exception as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"CosyVoice TTS failed after {max_retries} attempts: {e}")
            time.sleep(2 ** attempt)

    # Get audio duration via ffprobe
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
        "audio_path": output_path,
        "duration_seconds": duration,
    }
