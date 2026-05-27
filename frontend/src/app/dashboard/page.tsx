"use client";

import { useTasks } from "@/hooks/use-tasks";
import { useAuth } from "@/hooks/use-auth";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Video, CheckCircle, XCircle, Clock, ArrowRight } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

const STATUS_LABELS: Record<string, string> = {
  pending: "等待中",
  downloading: "下载中",
  extracting: "提取中",
  rewriting: "改写中",
  tts_synthesizing: "语音合成中",
  digital_human: "数字人生成中",
  compositing: "合成中",
  publishing: "发布中",
  completed: "已完成",
  failed: "失败",
  cancelled: "已取消",
};

export default function DashboardPage() {
  const { user } = useAuth();
  const { data, isLoading } = useTasks(1, 5);

  const tasks = data?.tasks || [];
  const totalTasks = data?.total || 0;
  const completed = tasks.filter((t) => t.status === "completed").length;
  const failed = tasks.filter((t) => t.status === "failed").length;
  const pending = tasks.filter(
    (t) => t.status !== "completed" && t.status !== "failed" && t.status !== "cancelled"
  ).length;

  const statusVariant = (status: string) => {
    switch (status) {
      case "completed": return "default" as const;
      case "failed": return "destructive" as const;
      case "pending": return "secondary" as const;
      case "cancelled": return "outline" as const;
      default: return "default" as const;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">
          欢迎回来，{user?.display_name || user?.username}
        </h1>
        <p className="text-muted-foreground">这是您的视频生产总览</p>
      </div>

      {/* Stats cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              任务总数
            </CardTitle>
            <Video className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <p className="text-2xl font-bold">{totalTasks}</p>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              已完成
            </CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{completed}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              进行中
            </CardTitle>
            <Clock className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{pending}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              失败
            </CardTitle>
            <XCircle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{failed}</p>
          </CardContent>
        </Card>
      </div>

      {/* Recent tasks */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">最近任务</h2>
        <Link href="/dashboard/tasks">
          <Button variant="ghost" size="sm" className="gap-1">
            查看全部 <ArrowRight className="h-4 w-4" />
          </Button>
        </Link>
      </div>

      {isLoading ? (
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-14 w-full" />
          ))}
        </div>
      ) : tasks.length === 0 ? (
        <Card className="py-12 text-center text-muted-foreground">
          <p>暂无任务，创建您的第一个视频生产任务！</p>
          <Link href="/dashboard/tasks">
            <Button className="mt-4">创建任务</Button>
          </Link>
        </Card>
      ) : (
        <div className="space-y-2">
          {tasks.map((task) => (
            <Link key={task.id} href={`/dashboard/tasks/${task.id}`}>
              <Card className="cursor-pointer transition-colors hover:bg-muted/50">
                <div className="flex items-center justify-between p-4">
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">
                      {task.source_video_url}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(task.created_at).toLocaleString("zh-CN")}
                    </p>
                  </div>
                  <Badge variant={statusVariant(task.status)} className="ml-4 shrink-0">
                    {STATUS_LABELS[task.status] || task.status}
                  </Badge>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
