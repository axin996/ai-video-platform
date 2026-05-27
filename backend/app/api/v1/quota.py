"""Quota and subscription routes."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.dependencies import get_current_user
from ...models import User, UserQuota, UserSubscription
from ...schemas import QuotaResponse, SubscriptionResponse

router = APIRouter()


@router.get("", response_model=QuotaResponse)
async def get_quota(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from datetime import date
    today = date.today()
    quota_month = today.replace(day=1)

    result = await db.execute(
        select(UserQuota).where(
            UserQuota.user_id == str(current_user.id),
            UserQuota.quota_month == quota_month,
        )
    )
    quota = result.scalar_one_or_none()
    if not quota:
        quota = UserQuota(
            user_id=str(current_user.id),
            quota_month=quota_month,
        )
        db.add(quota)
        await db.commit()
        await db.refresh(quota)

    return QuotaResponse.model_validate(quota)


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserSubscription)
        .where(UserSubscription.user_id == str(current_user.id))
        .order_by(UserSubscription.created_at.desc())
    )
    sub = result.scalar_one_or_none()
    if not sub:
        from datetime import datetime, timedelta, timezone
        sub = UserSubscription(
            user_id=str(current_user.id),
            plan_type="free",
            started_at=datetime.now(timezone.utc),
        )
        db.add(sub)
        await db.commit()
        await db.refresh(sub)

    return SubscriptionResponse.model_validate(sub)
