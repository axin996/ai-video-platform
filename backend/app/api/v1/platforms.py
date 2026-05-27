"""Platform account management and publishing routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.dependencies import get_current_user
from ...models import PlatformAccount, PublishRecord, User

router = APIRouter()

SUPPORTED_PLATFORMS = [
    {"platform": "douyin", "name": "抖音", "method": "playwright"},
    {"platform": "xhs", "name": "小红书", "method": "playwright"},
    {"platform": "shipinhao", "name": "视频号", "method": "playwright"},
    {"platform": "bilibili", "name": "B站", "method": "oauth2"},
    {"platform": "youtube", "name": "YouTube", "method": "oauth2"},
]


@router.get("")
async def list_platforms():
    return SUPPORTED_PLATFORMS


@router.get("/accounts")
async def list_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get platform accounts available to the current user."""
    result = await db.execute(
        select(PlatformAccount).where(
            (PlatformAccount.bound_user_id == str(current_user.id))
            | (PlatformAccount.account_type == "shared")
        )
    )
    accounts = result.scalars().all()
    return [{
        "id": str(a.id),
        "platform": a.platform,
        "account_name": a.account_name,
        "account_type": a.account_type,
        "status": a.status,
        "is_online": a.is_online,
        "daily_upload_limit": a.daily_upload_limit,
        "daily_upload_count": a.daily_upload_count,
    } for a in accounts]


@router.post("/accounts/{account_id}/login-qrcode")
async def get_login_qrcode(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get QR code URL for platform login. Stubbed — actual implementation uses Playwright."""
    result = await db.execute(select(PlatformAccount).where(PlatformAccount.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    # Placeholder: real implementation would open a Playwright page and capture QR code
    return {"platform": account.platform, "qrcode_url": "about:blank", "message": "QR code login initiation stubbed"}


@router.get("/publish-records")
async def list_publish_records(
    task_id: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(PublishRecord)
    if task_id:
        query = query.where(PublishRecord.task_id == task_id)
    result = await db.execute(query.order_by(PublishRecord.created_at.desc()))
    records = result.scalars().all()
    return [{
        "id": str(r.id),
        "task_id": str(r.task_id),
        "platform": r.platform,
        "title": r.title,
        "video_url": r.video_url,
        "video_id": r.video_id,
        "status": r.status,
        "error_message": r.error_message,
        "view_count": r.view_count,
        "like_count": r.like_count,
        "published_at": str(r.published_at) if r.published_at else None,
    } for r in records]
