export interface ResumeUploadResponse {
  resume_id: string;
  skills: string[];
  total_skills: number;
}

export interface SemanticMatch {
  resume_skill: string;
  jd_skill: string;
  similarity: number;
}

export interface JDMatchRequest {
  resume_id: string;
  job_description: string;
}

export interface JDMatchResponse {
  match_score: number;
  confidence: "high" | "medium" | "low";
  total_jd_skills: number;
  matching_skills: string[];
  semantic_matches: SemanticMatch[];
  missing_skills: string[];
  recommendations: string[];
  category_tips: Record<string, string>;
}

export interface JobRecommendation {
  title: string;
  company: string;
  location: string;
  match_score: number;
  matching_skills: string[];
  semantic_matches: SemanticMatch[];
  missing_skills: string[];
  recommendations: string[];
  redirect_url: string;
}

export interface RecommendJobsRequest {
  resume_id: string;
  query?: string;
  location?: string;
  top_n?: number;
}

export interface RecommendationsResponse {
  jobs: JobRecommendation[];
  total_jobs: number;
  resume_skills: string[];
}

export interface SkillGapRequest {
  resume_id: string;
  jd_text?: string;
}

export interface SkillGapResponse {
  resume_skills: string[];
  missing_skills: string[];
  semantic_gaps: SemanticMatch[];
  recommendations: string[];
  category_tips: Record<string, string>;
  match_score: number;
}
