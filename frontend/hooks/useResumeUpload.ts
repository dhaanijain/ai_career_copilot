"use client";

import { useState } from "react";
import { uploadResume } from "@/services/api";
import { useResume } from "@/context/ResumeContext";

type Stage = "idle" | "uploading" | "extracting" | "done" | "error";

const STAGE_MESSAGES: Record<Stage, string> = {
  idle: "",
  uploading: "Uploading resume...",
  extracting: "AI extracting skills...",
  done: "Skills extracted!",
  error: "Upload failed",
};

export function useResumeUpload() {
  const { setSession } = useResume();
  const [stage, setStage] = useState<Stage>("idle");
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);

  const upload = async (file: File) => {
    setError(null);
    setFileName(file.name);
    setStage("uploading");

    try {
      setStage("extracting");
      const res = await uploadResume(file);
      setSession({
        resumeId: res.resume_id,
        resumeSkills: res.skills,
        fileName: file.name,
      });
      setStage("done");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Unknown error";
      setError(msg);
      setStage("error");
    }
  };

  const reset = () => {
    setStage("idle");
    setError(null);
    setFileName(null);
  };

  return {
    upload,
    reset,
    stage,
    isProcessing: stage === "uploading" || stage === "extracting",
    isSuccess: stage === "done",
    statusMessage: STAGE_MESSAGES[stage],
    error,
    fileName,
  };
}
