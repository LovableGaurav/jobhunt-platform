"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type {
  Application,
  DashboardStats,
  JobPosting,
  User,
} from "@jobhunt/types";
import { api, ApiError, getStoredToken, setStoredToken } from "@/lib/api-client";

interface AppState {
  token: string | null;
  user: User | null;
  jobs: JobPosting[];
  matchedJobs: JobPosting[];
  applications: Application[];
  stats: DashboardStats | null;
  isLoading: boolean;
  error: string | null;

  setError: (error: string | null) => void;
  login: (email: string, password: string) => Promise<void>;
  register: (
    email: string,
    password: string,
    fullName: string,
  ) => Promise<void>;
  logout: () => void;
  hydrateUser: () => Promise<void>;
  fetchDashboard: () => Promise<void>;
  fetchJobs: () => Promise<void>;
  fetchMatchedJobs: () => Promise<void>;
  fetchApplications: () => Promise<void>;
  applyToJob: (jobId: string) => Promise<Application>;
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      jobs: [],
      matchedJobs: [],
      applications: [],
      stats: null,
      isLoading: false,
      error: null,

      setError: (error) => set({ error }),

      login: async (email, password) => {
        set({ isLoading: true, error: null });
        try {
          const { access_token } = await api.auth.login({ email, password });
          setStoredToken(access_token);
          set({ token: access_token });
          await get().hydrateUser();
          await get().fetchDashboard();
        } catch (e) {
          const message =
            e instanceof ApiError ? e.message : "Login failed";
          set({ error: message });
          throw e;
        } finally {
          set({ isLoading: false });
        }
      },

      register: async (email, password, fullName) => {
        set({ isLoading: true, error: null });
        try {
          await api.auth.register({
            email,
            password,
            full_name: fullName,
            target_roles: ["software engineer", "data scientist", "ml engineer"],
            years_experience: 0,
          });
          await get().login(email, password);
        } catch (e) {
          const message =
            e instanceof ApiError ? e.message : "Registration failed";
          set({ error: message });
          throw e;
        } finally {
          set({ isLoading: false });
        }
      },

      logout: () => {
        setStoredToken(null);
        set({
          token: null,
          user: null,
          jobs: [],
          matchedJobs: [],
          applications: [],
          stats: null,
          error: null,
        });
      },

      hydrateUser: async () => {
        const token = get().token ?? getStoredToken();
        if (!token) return;
        set({ token, isLoading: true, error: null });
        try {
          const user = await api.users.me(token);
          set({ user });
        } catch (e) {
          if (e instanceof ApiError && e.status === 401) {
            get().logout();
          } else {
            set({
              error: e instanceof ApiError ? e.message : "Failed to load profile",
            });
          }
        } finally {
          set({ isLoading: false });
        }
      },

      fetchDashboard: async () => {
        const { token } = get();
        if (!token) return;
        set({ isLoading: true, error: null });
        try {
          const stats = await api.dashboard.stats(token);
          set({ stats });
        } catch (e) {
          set({
            error:
              e instanceof ApiError ? e.message : "Failed to load dashboard",
          });
        } finally {
          set({ isLoading: false });
        }
      },

      fetchJobs: async () => {
        const { token } = get();
        if (!token) return;
        set({ isLoading: true, error: null });
        try {
          const jobs = await api.jobs.list(token, { limit: 50 });
          set({ jobs });
        } catch (e) {
          set({
            error: e instanceof ApiError ? e.message : "Failed to load jobs",
          });
        } finally {
          set({ isLoading: false });
        }
      },

      fetchMatchedJobs: async () => {
        const { token } = get();
        if (!token) return;
        set({ isLoading: true, error: null });
        try {
          const matchedJobs = await api.jobs.matches(token);
          set({ matchedJobs });
        } catch (e) {
          set({
            error:
              e instanceof ApiError ? e.message : "Failed to load matches",
          });
        } finally {
          set({ isLoading: false });
        }
      },

      fetchApplications: async () => {
        const { token } = get();
        if (!token) return;
        set({ isLoading: true, error: null });
        try {
          const applications = await api.applications.list(token);
          set({ applications });
        } catch (e) {
          set({
            error:
              e instanceof ApiError ? e.message : "Failed to load applications",
          });
        } finally {
          set({ isLoading: false });
        }
      },

      applyToJob: async (jobId) => {
        const { token } = get();
        if (!token) throw new Error("Not authenticated");
        const application = await api.applications.create(token, jobId);
        set((state) => ({
          applications: [application, ...state.applications],
        }));
        return application;
      },
    }),
    {
      name: "jobhunt-app",
      partialize: (state) => ({ token: state.token }),
      onRehydrateStorage: () => (state) => {
        if (state?.token) setStoredToken(state.token);
      },
    },
  ),
);
