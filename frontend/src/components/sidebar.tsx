"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import {
  LayoutDashboard,
  Video,
  Settings,
  LogOut,
  User,
} from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "总览", icon: LayoutDashboard },
  { href: "/dashboard/tasks", label: "任务管理", icon: Video },
  { href: "/dashboard/settings", label: "账号设置", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside className="fixed left-0 top-0 z-30 flex h-screen w-60 flex-col border-r bg-card">
      {/* Brand */}
      <div className="flex h-14 items-center gap-2 border-b px-4">
        <Video className="h-6 w-6 text-primary" />
        <span className="font-semibold text-sm">AI 视频平台</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-1 p-3">
        {navItems.map((item) => {
          const active = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link key={item.href} href={item.href}>
              <Button
                variant={active ? "secondary" : "ghost"}
                className={cn("w-full justify-start gap-2", active && "font-medium")}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </Button>
            </Link>
          );
        })}
      </nav>

      {/* User footer */}
      <div className="border-t p-3 space-y-2">
        <div className="flex items-center gap-2 px-2 text-sm text-muted-foreground">
          <User className="h-4 w-4" />
          <span className="truncate">{user?.email || "用户"}</span>
        </div>
        <Button
          variant="ghost"
          className="w-full justify-start gap-2 text-muted-foreground"
          onClick={logout}
        >
          <LogOut className="h-4 w-4" />
          退出登录
        </Button>
      </div>
    </aside>
  );
}
