"use client";

import { useState } from "react";
import { recommendJobs } from "@/services/api";
import { useResume } from "@/context/ResumeContext";

export function useJobRecommendations() {
  const { jobsData, setJobsData } = useResume();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState("");

  const fetch = async (
    resumeId: string,
    query?: string,
    location?: string,
    topN?: number,
    resumeSkills?: string[]
  ) => {
    setLoading(true);
    setError(null);
    setJobsData(null);

    try {
      setStatusMessage("Fetching live jobs from Adzuna...");
      const res = await recommendJobs({
        resume_id: resumeId,
        query,
        location,
        top_n: topN ?? 10,
        resume_skills: resumeSkills,
      });
      setStatusMessage("Ranking recommendations...");
      setJobsData(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to fetch recommendations");
    } finally {
      setLoading(false);
      setStatusMessage("");
    }
  };

  return { fetch, data: jobsData, loading, error, statusMessage };
}
