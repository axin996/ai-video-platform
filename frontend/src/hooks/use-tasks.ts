"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { TaskCreate, TaskListResponse, TaskResponse, TaskStatus } from "@/lib/types";

export function useTasks(page = 1, pageSize = 20, status?: TaskStatus) {
  return useQuery({
    queryKey: ["tasks", { page, pageSize, status }],
    queryFn: async () => {
      const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
      if (status) params.set("status", status);
      const { data } = await api.get<TaskListResponse>(`/tasks?${params}`);
      return data;
    },
  });
}

export function useTask(taskId: string | undefined) {
  return useQuery({
    queryKey: ["tasks", taskId],
    queryFn: async () => {
      const { data } = await api.get<TaskResponse>(`/tasks/${taskId}`);
      return data;
    },
    enabled: !!taskId,
  });
}

export function useCreateTask() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body: TaskCreate) => {
      const { data } = await api.post<TaskResponse>("/tasks", body);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });
}

export function useCancelTask() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (taskId: string) => {
      await api.delete(`/tasks/${taskId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });
}

export function useRetryTask() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ taskId, fromStep }: { taskId: string; fromStep?: string }) => {
      const { data } = await api.post<TaskResponse>(`/tasks/${taskId}/retry`, { from_step: fromStep });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });
}
