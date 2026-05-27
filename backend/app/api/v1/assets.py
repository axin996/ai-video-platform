"""Asset management routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.dependencies import get_current_user
from ...models import TaskAsset, User

router = APIRouter()


@router.get("/{asset_id}")
async def get_asset(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(TaskAsset).where(TaskAsset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    return {
        "id": str(asset.id),
        "task_id": str(asset.task_id),
        "asset_type": asset.asset_type,
        "file_name": asset.file_name,
        "file_url": asset.file_url,
        "file_size": asset.file_size,
        "mime_type": asset.mime_type,
        "metadata": asset.extra_metadata,
    }


@router.get("/{asset_id}/download")
async def download_asset(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a pre-signed download URL and redirect."""
    result = await db.execute(select(TaskAsset).where(TaskAsset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    if asset.file_url:
        return RedirectResponse(url=asset.file_url)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File URL not available")
