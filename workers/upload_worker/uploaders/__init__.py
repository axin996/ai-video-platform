"""Platform-specific uploaders for multi-platform publishing."""

from .base import BasePlatformUploader


def get_uploader(platform: str) -> BasePlatformUploader | None:
    """Factory to get the appropriate uploader for a platform."""
    if platform == "douyin":
        from .douyin import DouyinUploader
        return DouyinUploader()
    elif platform == "xhs":
        from .xiaohongshu import XiaohongshuUploader()
        return XiaohongshuUploader()
    elif platform == "shipinhao":
        from .shipinhao import ShipinhaoUploader()
        return ShipinhaoUploader()
    elif platform == "bilibili":
        from .bilibili import BilibiliUploader()
        return BilibiliUploader()
    elif platform == "youtube":
        from .youtube import YouTubeUploader()
        return YouTubeUploader()
    return None


__all__ = ["BasePlatformUploader", "get_uploader"]
