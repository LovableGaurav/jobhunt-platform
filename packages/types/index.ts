export type WorkMode = "remote" | "hybrid" | "onsite";
export type ExperienceLevel = "entry" | "junior" | "mid" | "senior";
export type ApplicationStatus =
  | "draft"
  | "queued"
  | "submitted"
  | "viewed"
  | "interview"
  | "rejected"
  | "offer"
  | "withdrawn";

export interface User {
  id: string;
  email: string;
  full_name: string;
  target_roles: string[];
  years_experience: number;
  resume_s3_key: string | null;
  created_at: string;
}

export interface JobPosting {
  id: string;
  external_id: string;
  source: string;
  title: string;
  company: string;
  location: string;
  work_mode: WorkMode;
  experience_level: ExperienceLevel;
  description: string;
  url: string;
  salary_min: number | null;
  salary_max: number | null;
  posted_at: string;
  match_score?: number;
}

export interface Application {
  id: string;
  job_id: string;
  user_id: string;
  status: ApplicationStatus;
  tailored_resume_key: string | null;
  cover_letter: string | null;
  match_score: number;
  applied_at: string | null;
  created_at: string;
  job?: JobPosting;
}

export interface AuthTokenResponse {
  access_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  target_roles?: string[];
  years_experience?: number;
}

export interface DashboardStats {
  total_jobs: number;
  matched_jobs: number;
  applications_submitted: number;
  interviews: number;
  match_rate: number;
}
