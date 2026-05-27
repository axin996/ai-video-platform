"""Douyin (抖音) uploader using Playwright browser automation."""

from .base import BasePlatformUploader, SessionExpiredError


class DouyinUploader(BasePlatformUploader):
    platform = "douyin"

    def upload(self, video_path: str, title: str, description: str = "",
               tags: list[str] | None = None) -> dict:
        """
        Upload video to Douyin Creator Platform.
        Uses stealth techniques to avoid detection:
        - Real Chrome (not Chromium)
        - stealth.min.js injection
        - headful mode with virtual display
        - Relative locators (get_by_text/get_by_role) instead of CSS selectors
        """
        # Implementation requires:
        # 1. Playwright async context manager
        # 2. Load stored session from platform_sessions table
        # 3. Navigate to https://creator.douyin.com/upload
        # 4. Upload file, fill metadata, click publish
        # 5. Extract video_id and video_url

        # Stub implementation — full version needs Chrome + stealth.js
        raise NotImplementedError(
            "Douyin uploader requires a running Chrome instance with remote debugging "
            "and a valid logged-in session. See docs/deployment.md for setup."
        )

    def verify_session(self) -> bool:
        raise NotImplementedError


# Alias
DouyinUploader
