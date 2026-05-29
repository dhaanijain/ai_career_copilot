"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";

interface ResumeSession {
  resumeId: string | null;
  resumeSkills: string[];
  fileName: string | null;
}

interface ResumeContextValue extends ResumeSession {
  setSession: (session: Partial<ResumeSession>) => void;
  clearSession: () => void;
}

const ResumeContext = createContext<ResumeContextValue | null>(null);

const STORAGE_KEY = "ai-copilot-resume-session";

export function ResumeProvider({ children }: { children: ReactNode }) {
  const [session, setSessionState] = useState<ResumeSession>({
    resumeId: null,
    resumeSkills: [],
    fileName: null,
  });

  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) setSessionState(JSON.parse(stored));
    } catch {}
  }, []);

  const setSession = (patch: Partial<ResumeSession>) => {
    setSessionState((prev) => {
      const next = { ...prev, ...patch };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      return next;
    });
  };

  const clearSession = () => {
    localStorage.removeItem(STORAGE_KEY);
    setSessionState({ resumeId: null, resumeSkills: [], fileName: null });
  };

  return (
    <ResumeContext.Provider
      value={{ ...session, setSession, clearSession }}
    >
      {children}
    </ResumeContext.Provider>
  );
}

export function useResume(): ResumeContextValue {
  const ctx = useContext(ResumeContext);
  if (!ctx) throw new Error("useResume must be used within ResumeProvider");
  return ctx;
}
