"use client";

import { useState } from "react";
import { matchJD } from "@/services/api";
import { JDMatchResponse } from "@/types";

export function useJDMatch() {
  const [result, setResult] = useState<JDMatchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = async (resumeId: string, jobDescription: string) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await matchJD({ resume_id: resumeId, job_description: jobDescription });
      setResult(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  return { analyze, result, loading, error };
}
