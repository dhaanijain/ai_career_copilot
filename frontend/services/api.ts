import { supabase } from "@/lib/supabase";
import type {
  ResumeUploadResponse,
  JDMatchRequest,
  JDMatchResponse,
  RecommendJobsRequest,
  RecommendationsResponse,
  SkillGapRequest,
  SkillGapResponse,
} from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getAuthHeaders(): Promise<HeadersInit> {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const authHeaders = await getAuthHeaders();
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      ...authHeaders,
      ...options.headers,
    },
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }

  return res.json();
}

export async function uploadResume(file: File): Promise<ResumeUploadResponse> {
  const form = new FormData();
  form.append("file", file);
  return request<ResumeUploadResponse>("/upload-resume", {
    method: "POST",
    body: form,
  });
}

export async function matchJD(body: JDMatchRequest): Promise<JDMatchResponse> {
  return request<JDMatchResponse>("/match-jd", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function recommendJobs(
  body: RecommendJobsRequest
): Promise<RecommendationsResponse> {
  return request<RecommendationsResponse>("/recommend-jobs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function analyzeSkillGap(
  body: SkillGapRequest
): Promise<SkillGapResponse> {
  return request<SkillGapResponse>("/skill-gap", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}
