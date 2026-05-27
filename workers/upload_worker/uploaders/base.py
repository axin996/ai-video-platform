"""Base class for platform-specific video uploaders."""

from abc import ABC, abstractmethod
from typing import Any


class BasePlatformUploader(ABC):
    """Abstract base for all platform uploaders.

    Each platform implements:
    - upload(): publish a video to the platform
    - verify_session(): check if the current session is still valid
    - login_qrcode(): get a QR code URL for login
    """

    platform: str = "unknown"

    @abstractmethod
    def upload(self, video_path: str, title: str, description: str = "",
               tags: list[str] | None = None) -> dict[str, Any]:
        """
        Upload and publish video.

        Returns:
            {"video_id": str, "video_url": str, "status": str}
        """

    @abstractmethod
    def verify_session(self) -> bool:
        """Check if current browser session/cookie is still valid."""

    def login_qrcode(self) -> str | None:
        """Get login QR code URL. Returns None if not supported."""
        return None


class SessionExpiredError(Exception):
    """Raised when the platform session/cookie has expired."""
