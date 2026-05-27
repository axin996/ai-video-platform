"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Auth ────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    display_name: str | None
    avatar_url: str | None
    role: str
    status: str
    email_verified: bool
    created_at: datetime
    last_login_at: datetime | None

    model_config = {"from_attributes": True}


# ── Tasks ───────────────────────────────────────────

class PipelineParamsScriptRewrite(BaseModel):
    enabled: bool = True
    style: str = "professional"
    language: str = "zh"
    additional_instructions: str | None = None


class PipelineParamsVoiceClone(BaseModel):
    enabled: bool = True
    reference_audio_url: str | None = None
    speed: float = 1.0
    emotion: str = "neutral"


class PipelineParamsDigitalHuman(BaseModel):
    enabled: bool = True
    model_id: str | None = None
    background_color: str = "#FFFFFF"
    position: str = "center"


class PipelineParamsSubtitles(BaseModel):
    enabled: bool = True
    style: str = "bottom_center"
    font_size: int = 24
    font_color: str = "#FFFFFF"
    stroke_color: str = "#000000"


class PipelineParamsBGM(BaseModel):
    enabled: bool = False
    music_url: str | None = None
    volume: float = 0.3


class PipelineParamsCover(BaseModel):
    enabled: bool = True
    auto_generate: bool = True
    style_template: str | None = "modern"


class PipelineParams(BaseModel):
    script_rewrite: PipelineParamsScriptRewrite = PipelineParamsScriptRewrite()
    voice_clone: PipelineParamsVoiceClone = PipelineParamsVoiceClone()
    digital_human: PipelineParamsDigitalHuman = PipelineParamsDigitalHuman()
    subtitles: PipelineParamsSubtitles = PipelineParamsSubtitles()
    bgm: PipelineParamsBGM = PipelineParamsBGM()
    cover: PipelineParamsCover = PipelineParamsCover()


class TaskCreate(BaseModel):
    source_video_url: str
    pipeline_params: PipelineParams = PipelineParams()
    publish_targets: list[str] = []
    scheduled_publish_at: datetime | None = None
    webhook_url: str | None = None
    tags: list[str] | None = None

    @field_validator("publish_targets")
    @classmethod
    def validate_targets(cls, v: list[str]) -> list[str]:
        valid = {"douyin", "xhs", "shipinhao", "bilibili", "youtube"}
        for target in v:
            if target not in valid:
                raise ValueError(f"Invalid platform: {target}. Must be one of {valid}")
        return v


class TaskStepResponse(BaseModel):
    id: UUID
    step_name: str
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    duration_ms: int | None
    output_result: dict | None
    error_message: str | None
    retry_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class PublishRecordResponse(BaseModel):
    id: UUID
    platform: str
    title: str | None
    video_url: str | None
    video_id: str | None
    status: str
    error_message: str | None
    view_count: int
    like_count: int
    comment_count: int
    share_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskResponse(BaseModel):
    id: UUID
    user_id: UUID
    source_video_url: str
    source_video_duration: float | None
    pipeline_params: dict
    publish_targets: list
    status: str
    error_message: str | None
    output_video_url: str | None
    scheduled_publish_at: datetime | None
    published_at: datetime | None
    priority: int
    retry_count: int
    tags: list | None
    steps: list[TaskStepResponse] = []
    publish_records: list[PublishRecordResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    total: int
    page: int
    page_size: int


class TaskRetry(BaseModel):
    from_step: str | None = None  # Step name to retry from; if None, retry the failed step


# ── Assets ──────────────────────────────────────────

class AssetResponse(BaseModel):
    id: UUID
    task_id: UUID
    asset_type: str
    file_name: str
    file_url: str | None
    file_size: int | None
    mime_type: str | None
    extra_metadata: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Platforms ───────────────────────────────────────

class PlatformAccountResponse(BaseModel):
    id: UUID
    platform: str
    account_name: str
    account_type: str
    status: str
    is_online: bool
    daily_upload_limit: int
    daily_upload_count: int

    model_config = {"from_attributes": True}


class PlatformLoginQRCode(BaseModel):
    qrcode_url: str
    expires_at: datetime


class PlatformPublishRequest(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str | None = None
    tags: list[str] | None = None
    cover_url: str | None = None
    scheduled_at: datetime | None = None
    visibility: str = "public"


# ── Templates ───────────────────────────────────────

class TemplateCreate(BaseModel):
    name: str
    description: str | None = None
    category: str | None = None
    pipeline_params: PipelineParams
    is_public: bool = True


class TemplateResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    category: str | None
    pipeline_params: dict
    preset_covers: list | None
    preset_bgms: list | None
    is_public: bool
    created_by: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Webhooks ────────────────────────────────────────

class WebhookRegister(BaseModel):
    url: str
    secret: str | None = None
    events: list[str]  # task.completed, task.failed, publish.completed, etc.


class WebhookResponse(BaseModel):
    id: UUID
    url: str
    events: list
    is_active: bool
    last_triggered_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Quota ───────────────────────────────────────────

class QuotaResponse(BaseModel):
    video_generations_monthly: int
    video_generations_used: int
    video_length_minutes_monthly: int
    video_length_minutes_used: int
    publishing_count_monthly: int
    publishing_count_used: int
    quota_month: str

    model_config = {"from_attributes": True}


class SubscriptionResponse(BaseModel):
    id: UUID
    plan_type: str
    status: str
    started_at: datetime
    expires_at: datetime | None
    auto_renew: bool

    model_config = {"from_attributes": True}
