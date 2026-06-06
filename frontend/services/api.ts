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
const API_BASE = `${BASE_URL}/api/v1`;

// Default timeouts (milliseconds)
const DEFAULT_TIMEOUT_MS = 60_000;   // 60 s for analysis endpoints
const UPLOAD_TIMEOUT_MS  = 90_000;   // 90 s for resume upload (OCR can be slow)

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly errorCode: string,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function getAuthHeaders(): Promise<HeadersInit> {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  timeoutMs = DEFAULT_TIMEOUT_MS,
): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const authHeaders = await getAuthHeaders();
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      signal: controller.signal,
      headers: {
        ...authHeaders,
        ...options.headers,
      },
    });

    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new ApiError(
        res.status,
        body.error_code ?? "REQUEST_FAILED",
        body.detail ?? res.statusText,
      );
    }

    return res.json();
  } catch (err) {
    if (err instanceof ApiError) throw err;
    if ((err as Error).name === "AbortError") {
      throw new ApiError(408, "TIMEOUT", "Request timed out. Please try again.");
    }
    throw new ApiError(0, "NETWORK_ERROR", (err as Error).message ?? "Network error");
  } finally {
    clearTimeout(timer);
  }
}

export async function uploadResume(file: File): Promise<ResumeUploadResponse> {
  const form = new FormData();
  form.append("file", file);
  return request<ResumeUploadResponse>("/upload-resume", {
    method: "POST",
    body: form,
  }, UPLOAD_TIMEOUT_MS);
}

export async function matchJD(body: JDMatchRequest): Promise<JDMatchResponse> {
  return request<JDMatchResponse>("/match-jd", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function recommendJobs(
  body: RecommendJobsRequest,
): Promise<RecommendationsResponse> {
  return request<RecommendationsResponse>("/recommend-jobs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function analyzeSkillGap(
  body: SkillGapRequest,
): Promise<SkillGapResponse> {
  return request<SkillGapResponse>("/skill-gap", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}
