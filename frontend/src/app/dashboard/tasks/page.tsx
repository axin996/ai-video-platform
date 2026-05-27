"use client";

import { useState } from "react";
import Link from "next/link";
import { useTasks, useCreateTask, useCancelTask } from "@/hooks/use-tasks";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { Plus, Loader2, ExternalLink, Ban } from "lucide-react";
import type { TaskStatus } from "@/lib/types";

const PLATFORM_LABELS: Record<string, string> = {
  douyin: "抖音",        // 抖音
  xhs: "小红书",     // 小红书
  shipinhao: "视频号", // 视频号
  bilibili: "B站",           // B站
  youtube: "YouTube",
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

const STATUS_FILTERS: { value: TaskStatus | "all"; label: string }[] = [
  { value: "all", label: "全部" },
  { value: "pending", label: "等待中" },
  { value: "downloading", label: "下载中" },
  { value: "extracting", label: "提取中" },
  { value: "rewriting", label: "改写中" },
  { value: "tts_synthesizing", label: "语音合成" },
  { value: "digital_human", label: "数字人" },
  { value: "compositing", label: "合成中" },
  { value: "publishing", label: "发布中" },
  { value: "completed", label: "已完成" },
  { value: "failed", label: "失败" },
  { value: "cancelled", label: "已取消" },
];

const statusVariant = (status: string) => {
  switch (status) {
    case "completed": return "default" as const;
    case "failed": return "destructive" as const;
    case "cancelled": return "outline" as const;
    case "pending": return "secondary" as const;
    default: return "default" as const;
  }
};

export default function TasksPage() {
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<TaskStatus | "all">("all");
  const [showNewTask, setShowNewTask] = useState(false);
  const [videoUrl, setVideoUrl] = useState("");
  const [platforms, setPlatforms] = useState<string[]>([]);

  const { data, isLoading } = useTasks(page, 10, statusFilter === "all" ? undefined : statusFilter);
  const createTask = useCreateTask();
  const cancelTask = useCancelTask();

  const handleCreate = async () => {
    if (!videoUrl) return;
    try {
      await createTask.mutateAsync({
        source_video_url: videoUrl,
        publish_targets: platforms,
      });
      toast.success("任务创建成功");
      setShowNewTask(false);
      setVideoUrl("");
      setPlatforms([]);
    } catch {
      toast.error("任务创建失败");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">任务管理</h1>
          <p className="text-muted-foreground">管理您的视频生产流水线</p>
        </div>
        <Dialog open={showNewTask} onOpenChange={setShowNewTask}>
          <DialogTrigger asChild>
            <Button className="gap-1">
              <Plus className="h-4 w-4" />
              新建任务
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>创建新任务</DialogTitle>
              <DialogDescription>
                提交视频链接，启动 AI 流水线
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>视频 URL</Label>
                <Input
                  placeholder="https://example.com/video.mp4"
                  value={videoUrl}
                  onChange={(e) => setVideoUrl(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>目标平台</Label>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(PLATFORM_LABELS).map(([key, label]) => (
                    <Button
                      key={key}
                      variant={platforms.includes(key) ? "default" : "outline"}
                      size="sm"
                      onClick={() => {
                        setPlatforms((prev) =>
                          prev.includes(key) ? prev.filter((p) => p !== key) : [...prev, key]
                        );
                      }}
                    >
                      {label}
                    </Button>
                  ))}
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button
                onClick={handleCreate}
                disabled={!videoUrl || createTask.isPending}
              >
                {createTask.isPending && (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                )}
                创建
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Status filter tabs */}
      <div className="flex flex-wrap gap-2">
        {STATUS_FILTERS.map((f) => (
          <Button
            key={f.value}
            variant={statusFilter === f.value ? "secondary" : "outline"}
            size="sm"
            onClick={() => { setStatusFilter(f.value); setPage(1); }}
          >
            {f.label}
          </Button>
        ))}
      </div>

      {/* Task table */}
      {isLoading ? (
        <div className="space-y-2">
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </div>
      ) : !data || data.tasks.length === 0 ? (
        <Card className="py-12 text-center text-muted-foreground">
          <p>暂无任务</p>
        </Card>
      ) : (
        <>
          <div className="space-y-2">
            {data.tasks.map((task) => (
              <Card key={task.id} className="p-4">
                <div className="flex items-center justify-between gap-4">
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">
                      {task.source_video_url}
                    </p>
                    <div className="mt-1 flex flex-wrap gap-1">
                      {(task.publish_targets as string[] || []).map((p) => (
                        <Badge key={p} variant="outline" className="text-xs">
                          {PLATFORM_LABELS[p] || p}
                        </Badge>
                      ))}
                      {(task.tags || []).map((t) => (
                        <Badge key={t} variant="secondary" className="text-xs">
                          {t}
                        </Badge>
                      ))}
                    </div>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {new Date(task.created_at).toLocaleString("zh-CN")}
                      {task.retry_count > 0 && ` · 已重试 ${task.retry_count} 次`}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <Badge variant={statusVariant(task.status)}>
                      {STATUS_LABELS[task.status] || task.status}
                    </Badge>
                    <Link href={`/dashboard/tasks/${task.id}`}>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <ExternalLink className="h-4 w-4" />
                      </Button>
                    </Link>
                    {task.status !== "completed" &&
                      task.status !== "failed" &&
                      task.status !== "cancelled" && (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-destructive"
                          onClick={() => {
                            cancelTask.mutate(task.id);
                            toast.info("任务已取消");
                          }}
                        >
                          <Ban className="h-4 w-4" />
                        </Button>
                      )}
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              共 {data.total} 个任务
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
              >
                上一页
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={(page * 10) >= data.total}
                onClick={() => setPage((p) => p + 1)}
              >
                下一页
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
