"""Step 7: Multi-platform publishing using Playwright browser automation."""

from ..app import celery_app


@celery_app.task(bind=True, name="pipeline.publish", queue="upload_queue",
                  acks_late=True, soft_time_limit=600, time_limit=900)
def publish_to_platform(self, task_id: str, video_path: str, platform: str,
                         pipeline_params: dict) -> dict:
    """
    Publish the final video to a specific platform.
    Routes to the appropriate platform uploader based on platform name.
    Returns: {platform, video_id, video_url, status}
    """
    from ...upload_worker.uploaders import get_uploader

    uploader = get_uploader(platform)
    if not uploader:
        return {
            "platform": platform,
            "status": "failed",
            "error": f"Unsupported platform: {platform}",
        }

    # Generate title from pipeline params or default
    post_title = pipeline_params.get("post_title", f"AI数字人视频 #{task_id[:8]}")

    try:
        result = uploader.upload(
            video_path=video_path,
            title=post_title,
            description=pipeline_params.get("post_description", ""),
            tags=pipeline_params.get("tags", []),
        )
        return {
            "platform": platform,
            "status": "published",
            "video_id": result.get("video_id"),
            "video_url": result.get("video_url"),
        }
    except Exception as e:
        return {
            "platform": platform,
            "status": "failed",
            "error": str(e),
        }
