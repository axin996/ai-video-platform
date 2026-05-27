"""Task management API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...core.dependencies import get_current_user
from ...models import User
from ...schemas import (
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskRetry,
)
from ...services.task_service import TaskService

router = APIRouter()


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    body: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await TaskService.create_task(db, str(current_user.id), body)
    # Trigger Celery pipeline (stubbed — actual call needs Celery app)
    # run_pipeline.delay(str(task.id))
    return task


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tasks, total = await TaskService.get_tasks(
        db, str(current_user.id), page=page, page_size=page_size, status=status
    )
    return TaskListResponse(
        tasks=[TaskResponse.model_validate(t) for t in tasks],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await TaskService.get_task(db, task_id)
    if not task or str(task.user_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}")
async def cancel_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await TaskService.get_task(db, task_id)
    if not task or str(task.user_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    try:
        await TaskService.cancel_task(db, task)
        return {"status": "cancelled"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{task_id}/retry", response_model=TaskResponse)
async def retry_task(
    task_id: str,
    body: TaskRetry = TaskRetry(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await TaskService.get_task(db, task_id)
    if not task or str(task.user_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    try:
        task = await TaskService.retry_task(db, task, body.from_step)
        return TaskResponse.model_validate(task)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{task_id}/steps")
async def get_task_steps(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await TaskService.get_task(db, task_id)
    if not task or str(task.user_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return [{"step_name": s.step_name, "status": s.status, "duration_ms": s.duration_ms, "error_message": s.error_message} for s in task.steps]


@router.get("/{task_id}/assets")
async def get_task_assets(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await TaskService.get_task(db, task_id)
    if not task or str(task.user_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return [{"id": a.id, "asset_type": a.asset_type, "file_name": a.file_name, "file_url": a.file_url, "mime_type": a.mime_type} for a in task.assets]
