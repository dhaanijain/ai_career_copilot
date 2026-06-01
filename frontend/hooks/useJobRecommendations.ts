"use client";

import { useState } from "react";
import { recommendJobs } from "@/services/api";
import { RecommendationsResponse } from "@/types";

export function useJobRecommendations() {
  const [data, setData] = useState<RecommendationsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState("");

  const fetch = async (
    resumeId: string,
    query?: string,
    location?: string,
    topN?: number
  ) => {
    setLoading(true);
    setError(null);
    setData(null);

    try {
      setStatusMessage("Fetching live jobs from Adzuna...");
      const res = await recommendJobs({
        resume_id: resumeId,
        query,
        location,
        top_n: topN ?? 10,
      });
      setStatusMessage("Ranking recommendations...");
      setData(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to fetch recommendations");
    } finally {
      setLoading(false);
      setStatusMessage("");
    }
  };

  return { fetch, data, loading, error, statusMessage };
}
