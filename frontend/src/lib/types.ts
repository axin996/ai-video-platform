/** Shared types matching backend API schemas. */

export interface UserResponse {
  id: string;
  email: string;
  username: string;
  display_name: string | null;
  avatar_url: string | null;
  role: string;
  status: string;
  email_verified: boolean;
  created_at: string;
  last_login_at: string | null;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface TaskStepResponse {
  id: string;
  step_name: string;
  status: StepStatus;
  started_at: string | null;
  completed_at: string | null;
  duration_ms: number | null;
  output_result: Record<string, unknown> | null;
  error_message: string | null;
  retry_count: number;
  created_at: string;
}

export interface TaskResponse {
  id: string;
  user_id: string;
  source_video_url: string;
  source_video_duration: number | null;
  pipeline_params: PipelineParams;
  publish_targets: string[];
  status: TaskStatus;
  error_message: string | null;
  output_video_url: string | null;
  scheduled_publish_at: string | null;
  published_at: string | null;
  priority: number;
  retry_count: number;
  tags: string[] | null;
  steps: TaskStepResponse[];
  publish_records: PublishRecordResponse[];
  created_at: string;
  updated_at: string;
}

export interface TaskListResponse {
  tasks: TaskResponse[];
  total: number;
  page: number;
  page_size: number;
}

export interface PublishRecordResponse {
  id: string;
  platform: string;
  title: string | null;
  video_url: string | null;
  video_id: string | null;
  status: string;
  error_message: string | null;
  view_count: number;
  like_count: number;
  comment_count: number;
  share_count: number;
  created_at: string;
}

export interface PipelineParams {
  script_rewrite: { enabled: boolean; style: string; language: string; additional_instructions?: string | null };
  voice_clone: { enabled: boolean; reference_audio_url?: string | null; speed: number; emotion: string };
  digital_human: { enabled: boolean; model_id?: string | null; background_color: string; position: string };
  subtitles: { enabled: boolean; style: string; font_size: number; font_color: string; stroke_color: string };
  bgm: { enabled: boolean; music_url?: string | null; volume: number };
  cover: { enabled: boolean; auto_generate: boolean; style_template?: string | null };
}

export interface TaskCreate {
  source_video_url: string;
  pipeline_params?: Partial<PipelineParams>;
  publish_targets?: string[];
  scheduled_publish_at?: string | null;
  webhook_url?: string | null;
  tags?: string[] | null;
}

export type TaskStatus =
  | "pending" | "downloading" | "extracting" | "rewriting"
  | "tts_synthesizing" | "digital_human" | "compositing"
  | "publishing" | "completed" | "failed" | "cancelled";

export type StepStatus = "pending" | "running" | "completed" | "failed" | "skipped";

export interface AssetResponse {
  id: string;
  task_id: string;
  asset_type: string;
  file_name: string;
  file_url: string | null;
  file_size: number | null;
  mime_type: string | null;
  metadata: Record<string, unknown> | null;
}

export interface TaskRetry {
  from_step?: string | null;
}

export type Platform = "douyin" | "xhs" | "shipinhao" | "bilibili" | "youtube";
