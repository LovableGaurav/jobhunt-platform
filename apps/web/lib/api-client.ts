import type {
  Application,
  AuthTokenResponse,
  DashboardStats,
  JobPosting,
  LoginRequest,
  RegisterRequest,
  User,
} from "@jobhunt/types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ??
  "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public detail?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

type RequestOptions = RequestInit & { token?: string | null };

async function request<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { token, headers, ...rest } = options;
  const res = await fetch(`${API_BASE}${path}`, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
  });

  if (!res.ok) {
    let detail: unknown;
    try {
      detail = await res.json();
    } catch {
      detail = await res.text();
    }
    const message =
      typeof detail === "object" &&
      detail !== null &&
      "detail" in detail &&
      typeof (detail as { detail: unknown }).detail === "string"
        ? (detail as { detail: string }).detail
        : `Request failed (${res.status})`;
    throw new ApiError(message, res.status, detail);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  auth: {
    login: (body: LoginRequest) =>
      request<AuthTokenResponse>("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    register: (body: RegisterRequest) =>
      request<User>("/api/v1/auth/register", {
        method: "POST",
        body: JSON.stringify(body),
      }),
  },

  users: {
    me: (token: string) =>
      request<User>("/api/v1/users/me", { token }),
  },

  jobs: {
    list: (token: string, params?: { skip?: number; limit?: number }) => {
      const qs = new URLSearchParams();
      if (params?.skip != null) qs.set("skip", String(params.skip));
      if (params?.limit != null) qs.set("limit", String(params.limit));
      const query = qs.toString();
      return request<JobPosting[]>(
        `/api/v1/jobs${query ? `?${query}` : ""}`,
        { token },
      );
    },
    matches: (token: string, minScore = 0.7) =>
      request<JobPosting[]>(
        `/api/v1/jobs/matches?min_score=${minScore}`,
        { token },
      ),
    get: (token: string, jobId: string) =>
      request<JobPosting>(`/api/v1/jobs/${jobId}`, { token }),
  },

  applications: {
    list: (token: string) =>
      request<Application[]>("/api/v1/applications", { token }),
    create: (token: string, jobId: string) =>
      request<Application>("/api/v1/applications", {
        method: "POST",
        token,
        body: JSON.stringify({ job_id: jobId }),
      }),
    get: (token: string, id: string) =>
      request<Application>(`/api/v1/applications/${id}`, { token }),
  },

  dashboard: {
    stats: (token: string) =>
      request<DashboardStats>("/api/v1/dashboard/stats", { token }),
  },
};

export function setStoredToken(token: string | null) {
  if (typeof window === "undefined") return;
  if (token) localStorage.setItem("jobhunt_token", token);
  else localStorage.removeItem("jobhunt_token");
}

export function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("jobhunt_token");
}
