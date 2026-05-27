"""Task service - business logic for pipeline task management."""

from datetime import datetime, timezone

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import Task, TaskAsset, TaskStep
from ..schemas import TaskCreate


class TaskService:

    @staticmethod
    async def create_task(
        db: AsyncSession,
        user_id: str,
        body: TaskCreate,
    ) -> Task:
        task = Task(
            user_id=user_id,
            source_video_url=body.source_video_url,
            pipeline_params=body.pipeline_params.model_dump(),
            publish_targets=body.publish_targets,
            scheduled_publish_at=body.scheduled_publish_at,
            tags=body.tags,
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def get_tasks(
        db: AsyncSession,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> tuple[list[Task], int]:
        query = (
            select(Task)
            .where(Task.user_id == user_id)
            .options(selectinload(Task.steps), selectinload(Task.publish_records))
        )
        count_q = select(func.count()).select_from(Task).where(Task.user_id == user_id)

        if status:
            query = query.where(Task.status == status)
            count_q = count_q.where(Task.status == status)

        total = (await db.execute(count_q)).scalar() or 0

        query = query.order_by(desc(Task.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        tasks = (await db.execute(query)).scalars().all()
        return list(tasks), total

    @staticmethod
    async def get_task(db: AsyncSession, task_id: str) -> Task | None:
        result = await db.execute(
            select(Task)
            .where(Task.id == task_id)
            .options(selectinload(Task.steps), selectinload(Task.publish_records), selectinload(Task.assets))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def cancel_task(db: AsyncSession, task: Task) -> Task:
        if task.status not in ("pending", "downloading", "extracting", "rewriting",
                                "tts_synthesizing", "digital_human", "compositing"):
            raise ValueError("Task cannot be cancelled in its current state")

        task.status = "cancelled"
        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def retry_task(db: AsyncSession, task: Task, from_step: str | None = None) -> Task:
        if task.status != "failed":
            raise ValueError("Only failed tasks can be retried")

        task.status = "pending"
        task.retry_count += 1
        task.error_message = None

        # Reset the target step and all subsequent steps
        reset = False
        for step in task.steps:
            if from_step and step.step_name == from_step:
                reset = True
            if reset or not from_step:
                step.status = "pending"
                step.error_message = None

        if not from_step and task.steps:
            # Reset all steps
            for step in task.steps:
                step.status = "pending"
                step.error_message = None

        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def update_step_status(
        db: AsyncSession,
        task_id: str,
        step_name: str,
        status: str,
        output_result: dict | None = None,
        output_paths: list[str] | None = None,
        error_message: str | None = None,
        worker_id: str | None = None,
    ) -> TaskStep:
        result = await db.execute(
            select(TaskStep).where(
                TaskStep.task_id == task_id,
                TaskStep.step_name == step_name,
            )
        )
        step = result.scalar_one_or_none()

        if not step:
            step = TaskStep(task_id=task_id, step_name=step_name)
            db.add(step)

        step.status = status

        if status == "running" and not step.started_at:
            step.started_at = datetime.now(timezone.utc)

        if status == "completed":
            step.completed_at = datetime.now(timezone.utc)
            if step.started_at:
                step.duration_ms = int(
                    (step.completed_at - step.started_at).total_seconds() * 1000
                )
            if output_result:
                step.output_result = output_result
            if output_paths:
                step.output_paths = output_paths

        if status == "failed":
            step.error_message = error_message

        if worker_id:
            step.worker_id = worker_id

        await db.commit()
        await db.refresh(step)
        return step

    @staticmethod
    async def create_asset(
        db: AsyncSession,
        task_id: str,
        asset_type: str,
        file_name: str,
        file_path: str,
        file_url: str | None = None,
        file_size: int | None = None,
        mime_type: str | None = None,
        extra_metadata: dict | None = None,
    ) -> TaskAsset:
        asset = TaskAsset(
            task_id=task_id,
            asset_type=asset_type,
            file_name=file_name,
            file_path=file_path,
            file_url=file_url,
            file_size=file_size,
            mime_type=mime_type,
            extra_metadata=extra_metadata or {},
        )
        db.add(asset)
        await db.commit()
        await db.refresh(asset)
        return asset
