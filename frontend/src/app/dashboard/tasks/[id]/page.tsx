"use client";

import { useParams, useRouter } from "next/navigation";
import { useTask, useRetryTask, useCancelTask } from "@/hooks/use-tasks";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import {
  ArrowLeft,
  CheckCircle2,
  XCircle,
  Clock,
  Circle,
  RotateCw,
  Ban,
  ExternalLink,
  Download,
} from "lucide-react";
import type { StepStatus } from "@/lib/types";

const STEP_LABELS: Record<string, string> = {
  downloading: "视频下载",
  extracting: "文案提取（Whisper）",
  rewriting: "文案改写（DeepSeek）",
  tts_synthesizing: "语音合成（CosyVoice）",
  digital_human: "数字人生成（HeyGem）",
  compositing: "视频合成（FFmpeg）",
  publishing: "多平台发布",
};

const STATUS_LABELS: Record<string, string> = {
  pending: "等待中",
  downloading: "下载中",
  extracting: "文案提取中",
  rewriting: "文案改写中",
  tts_synthesizing: "语音合成中",
  digital_human: "数字人生成中",
  compositing: "视频合成中",
  publishing: "发布中",
  completed: "已完成",
  failed: "失败",
  cancelled: "已取消",
};

const STEP_STATUS_LABELS: Record<string, string> = {
  pending: "等待中",
  running: "运行中",
  completed: "已完成",
  failed: "失败",
  skipped: "已跳过",
};

const statusColor = (status: string) => {
  switch (status) {
    case "completed": return "text-green-500";
    case "running": return "text-blue-500";
    case "failed": return "text-red-500";
    case "cancelled": return "text-muted-foreground";
    default: return "text-muted-foreground";
  }
};

const StepIcon = ({ status }: { status: StepStatus }) => {
  switch (status) {
    case "completed": return <CheckCircle2 className="h-5 w-5 text-green-500" />;
    case "running": return <Clock className="h-5 w-5 animate-pulse text-blue-500" />;
    case "failed": return <XCircle className="h-5 w-5 text-red-500" />;
    case "skipped": return <Circle className="h-5 w-5 text-muted-foreground" strokeWidth={1} />;
    default: return <Circle className="h-5 w-5 text-muted-foreground" strokeWidth={1} />;
  }
};

export default function TaskDetailPage() {
  const params = useParams();
  const router = useRouter();
  const taskId = params.id as string;
  const { data: task, isLoading } = useTask(taskId);
  const retryTask = useRetryTask();
  const cancelTask = useCancelTask();

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!task) {
    return (
      <div className="space-y-4">
        <Button variant="ghost" onClick={() => router.back()}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          返回
        </Button>
        <Card className="py-12 text-center text-muted-foreground">
          <p>任务不存在</p>
        </Card>
      </div>
    );
  }

  const canCancel = task.status !== "completed" &&
    task.status !== "failed" &&
    task.status !== "cancelled";
  const canRetry = task.status === "failed";

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-xl font-bold">任务详情</h1>
            <p className="text-xs font-mono text-muted-foreground">{task.id}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {canRetry && (
            <Button
              variant="outline"
              size="sm"
              className="gap-1"
              onClick={async () => {
                await retryTask.mutateAsync({ taskId: task.id });
                toast.success("已发起重试");
              }}
              disabled={retryTask.isPending}
            >
              <RotateCw className="h-4 w-4" />
              重试
            </Button>
          )}
          {canCancel && (
            <Button
              variant="outline"
              size="sm"
              className="gap-1 text-destructive"
              onClick={async () => {
                await cancelTask.mutateAsync(task.id);
                toast.info("任务已取消");
              }}
            >
              <Ban className="h-4 w-4" />
              取消任务
            </Button>
          )}
        </div>
      </div>

      {/* Info cards */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">视频来源</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <p className="break-all text-sm">{task.source_video_url}</p>
            {task.output_video_url && (
              <a
                href={task.output_video_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-sm text-primary hover:underline"
              >
                查看成品视频 <ExternalLink className="h-3 w-3" />
              </a>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">任务状态</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Badge variant={
              task.status === "completed" ? "default" :
              task.status === "failed" ? "destructive" :
              task.status === "cancelled" ? "outline" : "secondary"
            }>
              {STATUS_LABELS[task.status] || task.status}
            </Badge>
            {task.error_message && (
              <p className="text-sm text-destructive">{task.error_message}</p>
            )}
            <p className="text-xs text-muted-foreground">
              创建时间: {new Date(task.created_at).toLocaleString("zh-CN")}
            </p>
            {task.publish_targets.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {task.publish_targets.map((p) => (
                  <Badge key={p} variant="outline" className="text-xs">{p}</Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Pipeline steps */}
      <Card>
        <CardHeader>
          <CardTitle>流水线进度</CardTitle>
          <CardDescription>逐步处理状态追踪</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-0">
            {Object.entries(STEP_LABELS).map(([stepName, label], idx) => {
              const step = task.steps.find((s) => s.step_name === stepName);
              const stepStatus = step?.status || "pending";
              return (
                <div key={stepName}>
                  <div className="flex items-center gap-4 py-3">
                    <StepIcon status={stepStatus as StepStatus} />
                    <div className="flex-1">
                      <p className={`text-sm font-medium ${statusColor(stepStatus)}`}>
                        第 {idx + 1} 步: {label}
                      </p>
                      {step?.duration_ms != null && (
                        <p className="text-xs text-muted-foreground">
                          耗时: {(step.duration_ms / 1000).toFixed(1)} 秒
                        </p>
                      )}
                      {step?.error_message && (
                        <p className="text-xs text-red-500">{step.error_message}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      {stepStatus !== "pending" && (
                        <Badge variant={
                          stepStatus === "completed" ? "default" :
                          stepStatus === "failed" ? "destructive" :
                          stepStatus === "running" ? "secondary" : "outline"
                        }>
                          {STEP_STATUS_LABELS[stepStatus] || stepStatus}
                        </Badge>
                      )}
                      {step?.output_result && (step!.output_result as Record<string, unknown>).output_path ? (
                        <Button variant="ghost" size="icon" className="h-8 w-8" asChild>
                          <a href={(step!.output_result as Record<string, unknown>).output_path as string} target="_blank" rel="noopener noreferrer">
                            <Download className="h-4 w-4" />
                          </a>
                        </Button>
                      ) : null}
                    </div>
                  </div>
                  {idx < Object.keys(STEP_LABELS).length - 1 && <Separator />}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Publish records */}
      {task.publish_records.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>发布记录</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {task.publish_records.map((record) => (
                <div key={record.id} className="flex items-center justify-between rounded-md border p-3">
                  <div>
                    <p className="text-sm font-medium capitalize">{record.platform}</p>
                    <p className="text-xs text-muted-foreground">
                      {record.title || "未命名"} · 播放: {record.view_count} · 点赞: {record.like_count}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={
                      record.status === "published" ? "default" :
                      record.status === "failed" ? "destructive" : "secondary"
                    }>
                      {record.status === "published" ? "已发布" :
                       record.status === "failed" ? "失败" : "发布中"}
                    </Badge>
                    {record.video_url && (
                      <a href={record.video_url} target="_blank" rel="noopener noreferrer">
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <ExternalLink className="h-4 w-4" />
                        </Button>
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
