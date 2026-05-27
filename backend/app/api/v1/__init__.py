"""API v1 router aggregation."""

from fastapi import APIRouter

from .auth import router as auth_router
from .tasks import router as tasks_router
from .assets import router as assets_router
from .platforms import router as platforms_router
from .templates import router as templates_router
from .webhooks import router as webhooks_router
from .quota import router as quota_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])
router.include_router(assets_router, prefix="/assets", tags=["Assets"])
router.include_router(platforms_router, prefix="/platforms", tags=["Platforms"])
router.include_router(templates_router, prefix="/templates", tags=["Templates"])
router.include_router(webhooks_router, prefix="/webhooks", tags=["Webhooks"])
router.include_router(quota_router, prefix="/quota", tags=["Quota"])
