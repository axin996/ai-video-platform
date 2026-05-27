"""Step 1: Download source video from URL."""

import hashlib
import os
import subprocess

from ..app import celery_app
from ...core.config import settings


@celery_app.task(bind=True, name="pipeline.download", queue="pipeline_queue",
                  acks_late=True, soft_time_limit=600, time_limit=900)
def download_video(self, task_id: str, source_video_url: str) -> dict:
    """
    Download source video to local storage.
    Supports: direct URL (yt-dlp for HLS/m3u8), YouTube (yt-dlp).
    Returns: {video_path, file_name, duration_seconds, file_size_bytes}
    """
    task_dir = os.path.join(settings.TEMP_DIR, task_id, "source")
    os.makedirs(task_dir, exist_ok=True)

    # Generate a deterministic file name from URL hash
    url_hash = hashlib.md5(source_video_url.encode()).hexdigest()[:12]
    output_template = os.path.join(task_dir, f"source_{url_hash}.mp4")

    # Try yt-dlp first (handles most video platforms)
    try:
        cmd = [
            "yt-dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--merge-output-format", "mp4",
            "-o", output_template,
            "--no-playlist",
            source_video_url,
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=600)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback: direct HTTP download
        import requests
        response = requests.get(source_video_url, stream=True, timeout=300)
        response.raise_for_status()
        with open(output_template, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

    file_size = os.path.getsize(output_template)

    # Get video duration via ffprobe
    duration = 0.0
    try:
        probe_cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            output_template,
        ]
        result = subprocess.run(probe_cmd, capture_output=True, text=True)
        duration = float(result.stdout.strip())
    except Exception:
        pass

    return {
        "video_path": output_template,
        "file_name": os.path.basename(output_template),
        "duration_seconds": duration,
        "file_size_bytes": file_size,
    }
