"""WeChat Video Account (视频号) uploader using Playwright browser automation."""

from .base import BasePlatformUploader


class ShipinhaoUploader(BasePlatformUploader):
    platform = "shipinhao"

    def upload(self, video_path: str, title: str, description: str = "",
               tags: list[str] | None = None) -> dict:
        """
        Upload to WeChat Video Account (视频号).
        Most aggressive headless detection — must use headful Chrome + real user agent.
        Session validity is short (~3 days), requires frequent re-login.
        """
        raise NotImplementedError(
            "Shipinhao uploader requires headful Chrome with real display, "
            "valid WeChat session, and anti-detection measures."
        )

    def verify_session(self) -> bool:
        raise NotImplementedError
