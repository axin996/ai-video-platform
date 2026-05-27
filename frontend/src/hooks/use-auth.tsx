"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { TokenResponse, UserResponse } from "@/lib/types";

interface AuthState {
  user: UserResponse | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

function setTokens(access: string, refresh: string) {
  localStorage.setItem("access_token", access);
  localStorage.setItem("refresh_token", refresh);
}

function clearTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [isReady, setIsReady] = useState(false);

  // Fetch current user (runs on mount if token exists)
  const { data: user, isLoading } = useQuery({
    queryKey: ["auth", "me"],
    queryFn: async () => {
      const { data } = await api.get<UserResponse>("/auth/me");
      return data;
    },
    retry: false,
    staleTime: 5 * 60 * 1000,
    enabled: typeof window !== "undefined" && !!localStorage.getItem("access_token"),
  });

  useEffect(() => {
    setIsReady(true);
  }, []);

  const loginMutation = useMutation({
    mutationFn: async (creds: { email: string; password: string }) => {
      const { data } = await api.post<TokenResponse>("/auth/login", creds);
      return data;
    },
    onSuccess: (data) => {
      setTokens(data.access_token, data.refresh_token);
      queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
    },
  });

  const registerMutation = useMutation({
    mutationFn: async (body: { email: string; username: string; password: string }) => {
      const { data } = await api.post<UserResponse>("/auth/register", body);
      return data;
    },
  });

  const login = useCallback(
    async (email: string, password: string) => {
      await loginMutation.mutateAsync({ email, password });
      router.push("/dashboard");
    },
    [loginMutation, router]
  );

  const register = useCallback(
    async (email: string, username: string, password: string) => {
      await registerMutation.mutateAsync({ email, username, password });
      router.push("/login");
    },
    [registerMutation, router]
  );

  const logout = useCallback(() => {
    clearTokens();
    queryClient.clear();
    router.push("/login");
  }, [queryClient, router]);

  return (
    <AuthContext.Provider
      value={{
        user: user ?? null,
        isLoading: !isReady || isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
