"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { useAuth } from "@/hooks/use-auth";

export default function SettingsPage() {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">账号设置</h1>
        <p className="text-muted-foreground">管理您的账户信息和偏好设置</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>个人信息</CardTitle>
          <CardDescription>您的账户基本信息</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label>邮箱</Label>
              <Input value={user?.email || ""} disabled />
            </div>
            <div className="space-y-2">
              <Label>用户名</Label>
              <Input value={user?.username || ""} disabled />
            </div>
            <div className="space-y-2">
              <Label>显示名称</Label>
              <Input value={user?.display_name || ""} disabled />
            </div>
            <div className="space-y-2">
              <Label>角色</Label>
              <Input value={user?.role === "admin" ? "管理员" : user?.role === "vip" ? "VIP 用户" : "普通用户"} disabled />
            </div>
          </div>
          <Separator />
          <div className="space-y-2">
            <Label>API 服务地址</Label>
            <Input value={process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000 (默认)"} disabled />
            <p className="text-xs text-muted-foreground">
              通过环境变量 NEXT_PUBLIC_API_URL 设置
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
