"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

function DropdownMenu({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = React.useState(false);
  return (
    <div className="relative">
      {React.Children.map(children, (child) => {
        if (!React.isValidElement(child)) return child;
        return React.cloneElement(child as React.ReactElement<Record<string, unknown>>, { open, setOpen });
      })}
    </div>
  );
}

function DropdownMenuTrigger({ children, open, setOpen, ...props }: {
  children: React.ReactNode;
  open?: boolean;
  setOpen?: (o: boolean) => void;
  [key: string]: unknown;
}) {
  return (
    <div onClick={() => setOpen?.(!open)} {...props}>
      {children}
    </div>
  );
}

function DropdownMenuContent({ children, className, open }: {
  children: React.ReactNode;
  className?: string;
  open?: boolean;
}) {
  if (!open) return null;
  return (
    <div className={cn("absolute right-0 z-50 mt-2 w-56 rounded-md border bg-popover p-1 shadow-md", className)}>
      {children}
    </div>
  );
}

function DropdownMenuItem({ children, className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none hover:bg-accent", className)} {...props}>
      {children}
    </div>
  );
}

export { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem };
