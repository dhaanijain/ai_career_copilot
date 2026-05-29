"use client";

import { useState } from "react";
import { analyzeSkillGap } from "@/services/api";
import { SkillGapResponse } from "@/types";

export function useSkillGap() {
  const [data, setData] = useState<SkillGapResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = async (resumeId: string, jdText?: string) => {
    setLoading(true);
    setError(null);

    try {
      const res = await analyzeSkillGap({ resume_id: resumeId, jd_text: jdText });
      setData(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  return { analyze, data, loading, error };
}
