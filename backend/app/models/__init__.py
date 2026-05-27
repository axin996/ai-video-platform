"""Database models for the AI Video Platform."""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=gen_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(200))
    avatar_url: Mapped[str | None] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(20), default="user")  # user, admin, vip
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, suspended, disabled
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=datetime.utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    preferences: Mapped[dict] = mapped_column(JSONB, default=dict)

    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("UserSubscription", back_populates="user", cascade="all, delete-orphan")
    quotas = relationship("UserQuota", back_populates="user", cascade="all, delete-orphan")
    webhooks = relationship("Webhook", back_populates="user", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    source_video_url: Mapped[str] = mapped_column(Text, nullable=False)
    source_video_path: Mapped[str | None] = mapped_column(Text)
    source_video_duration: Mapped[float | None] = mapped_column(Float)

    pipeline_params: Mapped[dict] = mapped_column(JSONB, default=dict)
    publish_targets: Mapped[list] = mapped_column(JSONB, default=list)

    status: Mapped[str] = mapped_column(
        String(30),
        default="pending",
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(Text)

    output_video_path: Mapped[str | None] = mapped_column(Text)
    output_video_url: Mapped[str | None] = mapped_column(Text)
    output_duration: Mapped[float | None] = mapped_column(Float)
    output_size_bytes: Mapped[int | None] = mapped_column(Integer)

    scheduled_publish_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    priority: Mapped[int] = mapped_column(Integer, default=0)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    tags: Mapped[list | None] = mapped_column(ARRAY(Text))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','downloading','extracting','rewriting','tts_synthesizing','digital_human','compositing','publishing','completed','failed','cancelled')",
            name="valid_task_status",
        ),
    )

    user = relationship("User", back_populates="tasks")
    steps = relationship("TaskStep", back_populates="task", cascade="all, delete-orphan", order_by="TaskStep.created_at", lazy="selectin")
    assets = relationship("TaskAsset", back_populates="task", cascade="all, delete-orphan", lazy="selectin")
    publish_records = relationship("PublishRecord", back_populates="task", cascade="all, delete-orphan", lazy="selectin")


class TaskStep(Base):
    __tablename__ = "task_steps"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=gen_uuid)
    task_id: Mapped[str] = mapped_column(UUID, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    step_name: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    input_params: Mapped[dict | None] = mapped_column(JSONB)
    output_result: Mapped[dict | None] = mapped_column(JSONB)
    output_paths: Mapped[list | None] = mapped_column(ARRAY(Text))
    error_message: Mapped[str | None] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    worker_id: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))

    __table_args__ = (
        UniqueConstraint("task_id", "step_name"),
        CheckConstraint("status IN ('pending','running','completed','failed','skipped')", name="valid_step_status"),
    )

    task = relationship("Task", back_populates="steps")


class TaskAsset(Base):
    __tablename__ = "task_assets"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=gen_uuid)
    task_id: Mapped[str] = mapped_column(UUID, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_type: Mapped[str] = mapped_column(String(30), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_url: Mapped[str | None] = mapped_column(Text)
    file_size: Mapped[int | None] = mapped_column(Integer)
    mime_type: Mapped[str | None] = mapped_column(String(100))
    extra_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))

    task = relationship("Task", back_populates="assets")


class PlatformAccount(Base):
    __tablename__ = "platform_accounts"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=gen_uuid)
    platform: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    account_name: Mapped[str] = mapped_column(String(200), nullable=False)
    account_type: Mapped[str] = mapped_column(String(20), default="shared")  # shared, dedicated
    status: Mapped[str] = mapped_column(String(20), default="active")
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    login_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    bound_user_id: Mapped[str | None] = mapped_column(UUID, ForeignKey("users.id"), nullable=True)
    bound_user_note: Mapped[str | None] = mapped_column(Text)
    daily_upload_limit: Mapped[int] = mapped_column(Integer, default=10)
    daily_upload_count: Mapped[int] = mapped_column(Integer, default=0)
    last_upload_reset_at: Mapped[datetime | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("platform", "account_name"),
    )

    sessions = relationship("PlatformSession", back_populates="account", cascade="all, delete-orphan")
    publish_records = relationship("PublishRecord", back_populates="account")


class PlatformSession(Base):
    __tablename__ = "platform_sessions"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=gen_uuid)
    account_id: Mapped[str] = mapped_column(UUID, ForeignKey("platform_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(30), nullable=False)
    session_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    user_agent: Mapped[str | None] = mapped_column(String(500))
    login_method: Mapped[str | None] = mapped_column(String(20))
    qrcode_url: Mapped[str | None] = mapped_column(Text)
    qrcode_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))

    account = relationship("PlatformAccount", back_populates="sessions")


class PublishRecord(Base):
    __tablename__ = "publish_records"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=gen_uuid)
    task_id: Mapped[str] = mapped_column(UUID, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id: Mapped[str] = mapped_column(UUID, ForeignKey("platform_accounts.id"), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    video_url: Mapped[str | None] = mapped_column(Text)
    video_id: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    error_message: Mapped[str | None] = mapped_column(Text)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)
    share_count: Mapped[int] = mapped_column(Integer, default=0)
    statistics_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint("status IN ('pending','uploading','published','failed')", name="valid_publish_status"),
    )

    task = relationship("Task", back_populates="publish_records")
    account = relationship("PlatformAccount", back_populates="publish_records")


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=True)
    payment_provider: Mapped[str | None] = mapped_column(String(30))
    payment_id: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))

    user = relationship("User", back_populates="subscriptions")


class UserQuota(Base):
    __tablename__ = "user_quotas"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    video_generations_monthly: Mapped[int] = mapped_column(Integer, default=5)
    video_generations_used: Mapped[int] = mapped_column(Integer, default=0)
    video_length_minutes_monthly: Mapped[int] = mapped_column(Integer, default=30)
    video_length_minutes_used: Mapped[int] = mapped_column(Integer, default=0)
    publishing_count_monthly: Mapped[int] = mapped_column(Integer, default=10)
    publishing_count_used: Mapped[int] = mapped_column(Integer, default=0)
    quota_month: Mapped[datetime] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "quota_month"),
    )

    user = relationship("User", back_populates="quotas")


class Template(Base):
    __tablename__ = "templates"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(50))
    pipeline_params: Mapped[dict] = mapped_column(JSONB, nullable=False)
    preset_covers: Mapped[list | None] = mapped_column(ARRAY(Text))
    preset_bgms: Mapped[list | None] = mapped_column(JSONB)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[str | None] = mapped_column(UUID, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=datetime.utcnow)


class Webhook(Base):
    __tablename__ = "webhooks"

    id: Mapped[str] = mapped_column(UUID, primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    secret: Mapped[str | None] = mapped_column(String(255))
    events: Mapped[list] = mapped_column(ARRAY(Text), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_triggered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))

    user = relationship("User", back_populates="webhooks")
