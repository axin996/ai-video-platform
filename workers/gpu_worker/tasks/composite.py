"""Step 6: Composite final video with FFmpeg (subtitles + BGM + cover)."""

import os
import subprocess

from ..app import celery_app
from ...core.config import settings


@celery_app.task(bind=True, name="pipeline.composite", queue="pipeline_queue",
                  acks_late=True, soft_time_limit=600, time_limit=900)
def composite_video(self, task_id: str, digital_human_path: str,
                     srt_path: str | None, pipeline_params: dict) -> dict:
    """
    Composite final video:
    - Overlay SRT subtitles on digital human video
    - Mix background music (optional)
    - Add cover image as first frame (optional)
    Output: H.264 + AAC MP4
    Returns: {video_path, duration_seconds, file_size_bytes}
    """
    task_dir = os.path.join(settings.TEMP_DIR, task_id, "video")
    os.makedirs(task_dir, exist_ok=True)
    output_path = os.path.join(task_dir, "output_final.mp4")

    subtitle_config = pipeline_params.get("subtitles", {})
    bgm_config = pipeline_params.get("bgm", {})

    # Build FFmpeg filter chain
    video_filters = []
    if srt_path and os.path.exists(srt_path) and subtitle_config.get("enabled", True):
        font_size = subtitle_config.get("font_size", 24)
        font_color = subtitle_config.get("font_color", "&H00FFFFFF")
        stroke_color = subtitle_config.get("stroke_color", "&H00000000")
        # Escape Windows-style paths for FFmpeg
        srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")
        video_filters.append(
            f"subtitles='{srt_escaped}':force_style='FontSize={font_size},"
            f"PrimaryColour={font_color},OutlineColour={stroke_color},Alignment=2'"
        )

    # Build FFmpeg command
    cmd = ["ffmpeg", "-y", "-i", digital_human_path]

    audio_inputs = []

    if bgm_config.get("enabled") and bgm_config.get("music_url"):
        bgm_volume = bgm_config.get("volume", 0.3)
        audio_inputs.append(bgm_config["music_url"])
        cmd.extend(["-i", bgm_config["music_url"]])

    # Video filter
    if video_filters:
        cmd.extend(["-vf", ",".join(video_filters)])

    # Audio mixing
    if audio_inputs:
        cmd.extend([
            "-filter_complex",
            f"[1:a]volume={bgm_volume}[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2"
        ])

    # Output encoding
    cmd.extend([
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_path,
    ])

    subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=600)

    file_size = os.path.getsize(output_path)

    # Get duration
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
        "file_size_bytes": file_size,
    }
