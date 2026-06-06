"use client";

import { useState } from "react";
import { analyzeSkillGap } from "@/services/api";
import { useResume } from "@/context/ResumeContext";

export function useSkillGap() {
  const { skillGapData, setSkillGapData } = useResume();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = async (resumeId: string, jdText?: string, resumeSkills?: string[]) => {
    setLoading(true);
    setError(null);

    try {
      const res = await analyzeSkillGap({
        resume_id: resumeId,
        jd_text: jdText,
        resume_skills: resumeSkills,
      });
      setSkillGapData(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  return { analyze, data: skillGapData, loading, error };
}
