"""YouTube uploader using YouTube Data API v3 (OAuth2)."""

from .base import BasePlatformUploader


class YouTubeUploader(BasePlatformUploader):
    platform = "youtube"

    def upload(self, video_path: str, title: str, description: str = "",
               tags: list[str] | None = None) -> dict:
        """
        Upload to YouTube via Data API v3 with OAuth2.
        The most stable platform integration — no Playwright needed.
        """
        # YouTube Data API v3:
        # POST https://www.googleapis.com/upload/youtube/v3/videos
        # with OAuth2 access_token
        #
        # Use google-api-python-client or google-auth libraries
        raise NotImplementedError(
            "YouTube uploader requires OAuth2 credentials (client_id, client_secret). "
            "Register at https://console.cloud.google.com/apis/credentials"
        )

    def verify_session(self) -> bool:
        # OAuth2 refresh tokens are long-lived
        raise NotImplementedError
