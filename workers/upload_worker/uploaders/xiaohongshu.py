"""Xiaohongshu (小红书) uploader using Playwright browser automation."""

from .base import BasePlatformUploader


class XiaohongshuUploader(BasePlatformUploader):
    platform = "xhs"

    def upload(self, video_path: str, title: str, description: str = "",
               tags: list[str] | None = None) -> dict:
        """
        Upload to Xiaohongshu Creator Platform.
        Note: Requires >= 30s interval between uploads to avoid rate limiting.
        API signing (x-s, x-t headers) may require additional library support.
        """
        raise NotImplementedError(
            "Xiaohongshu uploader requires a running Chrome instance with remote debugging "
            "and a valid logged-in session."
        )

    def verify_session(self) -> bool:
        raise NotImplementedError
