"""Bilibili (B站) uploader using OAuth2 API (primary) + Playwright fallback."""

from .base import BasePlatformUploader


class BilibiliUploader(BasePlatformUploader):
    platform = "bilibili"

    def upload(self, video_path: str, title: str, description: str = "",
               tags: list[str] | None = None) -> dict:
        """
        Upload to Bilibili via Open Platform API (preferred).
        Uses OAuth2 for authentication — no Playwright needed for the primary flow.
        Fallback: Playwright browser automation if API upload fails.
        """
        # Bilibili Open API:
        # POST https://member.bilibili.com/x/vu/client/add
        # with access_token (OAuth2)
        raise NotImplementedError(
            "Bilibili uploader requires OAuth2 credentials (client_id, client_secret). "
            "Register at https://openhome.bilibili.com/"
        )

    def verify_session(self) -> bool:
        # Bilibili OAuth2 tokens last ~30 days with refresh
        raise NotImplementedError
