"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAppStore } from "@/stores/app-store";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { token, user, hydrateUser, isLoading } = useAppStore();

  useEffect(() => {
    if (!token) {
      router.replace("/login");
      return;
    }
    if (!user) void hydrateUser();
  }, [token, user, hydrateUser, router]);

  if (!token || (!user && isLoading)) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-brand-600 border-t-transparent" />
      </div>
    );
  }

  if (!user) return null;

  return <>{children}</>;
}
