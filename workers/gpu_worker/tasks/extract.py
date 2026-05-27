"""Step 2: Extract audio and transcribe with Whisper."""

import json
import os
import subprocess

from ..app import celery_app
from ...core.config import settings
from ..app import whisper_model  # Preloaded at worker startup


@celery_app.task(bind=True, name="pipeline.extract", queue="pipeline_queue",
                  acks_late=True, soft_time_limit=900, time_limit=1200)
def extract_script(self, task_id: str, video_path: str) -> dict:
    """
    Extract narration script from video using Whisper ASR.
    1. Extract audio track with FFmpeg
    2. Transcribe with faster-whisper
    3. Generate SRT subtitles
    Returns: {script_text, srt_content, duration_seconds, segments[]}
    """
    task_dir = os.path.join(settings.TEMP_DIR, task_id, "audio")
    os.makedirs(task_dir, exist_ok=True)

    audio_path = os.path.join(task_dir, "extracted_audio.wav")

    # Step 1: Extract audio (16kHz mono WAV for Whisper)
    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        audio_path,
    ], check=True, capture_output=True, text=True)

    # Step 2: Transcribe with Whisper
    segments = []
    full_text = ""

    if whisper_model is None:
        raise RuntimeError("Whisper model not loaded. GPU worker requires faster-whisper.")

    whisper_segments, info = whisper_model.transcribe(
        audio_path,
        beam_size=5,
        language="zh",
        vad_filter=True,
    )

    for seg in whisper_segments:
        segments.append({
            "start": round(seg.start, 3),
            "end": round(seg.end, 3),
            "text": seg.text.strip(),
        })
        full_text += seg.text

    duration = info.duration

    # Step 3: Generate SRT subtitle file
    srt_path = os.path.join(task_dir.replace("audio", "subtitle"), "subtitle.srt")
    os.makedirs(os.path.dirname(srt_path), exist_ok=True)
    srt_content = _generate_srt(segments)
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    # Save script as JSON
    script_dir = os.path.join(settings.TEMP_DIR, task_id, "script")
    os.makedirs(script_dir, exist_ok=True)
    script_path = os.path.join(script_dir, "original_script.json")
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump({"text": full_text, "segments": segments, "duration": duration}, f, ensure_ascii=False)

    return {
        "script_text": full_text,
        "segments": segments,
        "duration_seconds": duration,
        "audio_path": audio_path,
        "srt_path": srt_path,
        "script_path": script_path,
    }


def _generate_srt(segments: list[dict]) -> str:
    """Convert segments to SRT format."""
    lines = []
    for i, seg in enumerate(segments, 1):
        start_ts = _seconds_to_srt_time(seg["start"])
        end_ts = _seconds_to_srt_time(seg["end"])
        lines.append(f"{i}")
        lines.append(f"{start_ts} --> {end_ts}")
        lines.append(seg["text"])
        lines.append("")
    return "\n".join(lines)


def _seconds_to_srt_time(seconds: float) -> str:
    """Convert seconds to SRT timestamp format HH:MM:SS,mmm."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
