"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  GitCompare, AlertCircle, Sparkles, CheckCircle2, XCircle, ArrowRight
} from "lucide-react";
import { useResume } from "@/context/ResumeContext";
import { useJDMatch } from "@/hooks/useJDMatch";
import MatchRing from "@/components/ui/MatchRing";
import SkillChip from "@/components/ui/SkillChip";
import AIInsightCard from "@/components/ui/AIInsightCard";
import GradientButton from "@/components/ui/GradientButton";
import AnalyticsCard from "@/components/ui/AnalyticsCard";

const EXAMPLE_JD = `We are looking for a Machine Learning Engineer with:
- 3+ years Python experience
- PyTorch or TensorFlow for model training
- MLflow or similar for experiment tracking
- Docker and Kubernetes for deployment
- Experience with LLMs, RAG pipelines, or Transformers
- Familiarity with AWS or GCP
- Strong fundamentals in statistics and linear algebra`;

const CONFIDENCE_COLORS = {
  high: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
  medium: "text-yellow-400 bg-yellow-500/10 border-yellow-500/20",
  low: "text-red-400 bg-red-500/10 border-red-500/20",
};

export default function JDMatchPage() {
  const { resumeId } = useResume();
  const { analyze, result, loading, error } = useJDMatch();
  const [jd, setJd] = useState("");

  const handleAnalyze = () => {
    if (!resumeId || !jd.trim()) return;
    analyze(resumeId, jd);
  };

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
        <div className="flex items-center gap-2 text-purple-400 text-sm font-medium mb-2">
          <GitCompare className="w-4 h-4" />
          JD Match
        </div>
        <h1 className="font-display font-bold text-3xl text-white">Job Description Matcher</h1>
        <p className="text-[#A1A1AA] text-sm mt-1.5">
          Paste any job description to get exact + semantic match analysis against your resume.
        </p>
      </motion.div>

      {!resumeId && (
        <div className="mb-6 flex items-center gap-3 bg-yellow-500/5 border border-yellow-500/20 rounded-2xl p-4 text-yellow-400 text-sm">
          <AlertCircle className="w-4 h-4 shrink-0" />
          Upload your resume first to use JD matching.
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Input */}
        <div className="space-y-4">
          <div className="bg-[#111114] border border-white/[0.08] rounded-2xl p-5">
            <div className="flex items-center justify-between mb-3">
              <label className="text-sm font-semibold text-white">Job Description</label>
              <button
                onClick={() => setJd(EXAMPLE_JD)}
                className="text-xs text-purple-400 hover:text-purple-300 transition-colors"
              >
                Load example
              </button>
            </div>
            <textarea
              value={jd}
              onChange={(e) => setJd(e.target.value)}
              placeholder="Paste the full job description here..."
              rows={14}
              className="w-full bg-[#18181C] border border-white/[0.08] rounded-xl p-4 text-sm text-white placeholder-[#A1A1AA] outline-none focus:border-purple-500/40 resize-none transition-colors leading-relaxed"
            />
            <div className="flex items-center justify-between mt-3">
              <span className="text-xs text-[#A1A1AA]">{jd.length} characters</span>
              <GradientButton
                onClick={handleAnalyze}
                disabled={!resumeId || !jd.trim() || loading}
                loading={loading}
              >
                <Sparkles className="w-4 h-4" />
                Analyze Match
              </GradientButton>
            </div>
          </div>

          {error && (
            <div className="flex items-center gap-3 bg-red-500/5 border border-red-500/20 rounded-2xl p-4 text-red-400 text-sm">
              <AlertCircle className="w-4 h-4 shrink-0" />
              {error}
            </div>
          )}
        </div>

        {/* Results */}
        <div className="space-y-4">
          <AnimatePresence mode="wait">
            {result ? (
              <motion.div
                key="results"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="space-y-4"
              >
                {/* Score ring */}
                <div className="bg-[#111114] border border-white/[0.08] rounded-2xl p-6 flex flex-col items-center gap-4">
                  <MatchRing score={result.match_score} size={140} strokeWidth={10} label="Overall Match" />

                  <div className="flex items-center gap-3">
                    <span className={`text-xs font-semibold px-3 py-1 rounded-full border ${CONFIDENCE_COLORS[result.confidence]}`}>
                      {result.confidence.toUpperCase()} CONFIDENCE
                    </span>
                    <span className="text-xs text-[#A1A1AA]">
                      {result.total_jd_skills} JD skills analyzed
                    </span>
                  </div>
                </div>

                {/* Analytics */}
                <div className="grid grid-cols-2 gap-3">
                  <AnalyticsCard
                    label="Exact Matches"
                    value={result.matching_skills.length}
                    icon={<CheckCircle2 className="w-4 h-4" />}
                    color="green"
                  />
                  <AnalyticsCard
                    label="Skill Gaps"
                    value={result.missing_skills.length}
                    icon={<XCircle className="w-4 h-4" />}
                    color="red"
                  />
                </div>

                {/* Matching skills */}
                {result.matching_skills.length > 0 && (
                  <div className="bg-[#111114] border border-white/[0.08] rounded-2xl p-5">
                    <div className="flex items-center gap-2 mb-3">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      <h4 className="font-semibold text-white text-sm">Matching Skills</h4>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {result.matching_skills.map((s) => (
                        <SkillChip key={s} skill={s} variant="match" animate />
                      ))}
                    </div>
                  </div>
                )}

                {/* Semantic matches */}
                {result.semantic_matches.length > 0 && (
                  <div className="bg-[#111114] border border-white/[0.08] rounded-2xl p-5">
                    <div className="flex items-center gap-2 mb-3">
                      <ArrowRight className="w-4 h-4 text-blue-400" />
                      <h4 className="font-semibold text-white text-sm">Semantic Matches</h4>
                    </div>
                    <div className="space-y-2">
                      {result.semantic_matches.slice(0, 5).map((sm, i) => (
                        <div key={i} className="flex items-center justify-between text-sm">
                          <div className="flex items-center gap-2">
                            <SkillChip skill={sm.resume_skill} variant="neutral" size="sm" />
                            <span className="text-[#A1A1AA]">≈</span>
                            <SkillChip skill={sm.jd_skill} variant="semantic" size="sm" />
                          </div>
                          <span className="text-xs text-[#A1A1AA]">
                            {Math.round(sm.similarity * 100)}%
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Missing skills */}
                {result.missing_skills.length > 0 && (
                  <div className="bg-[#111114] border border-white/[0.08] rounded-2xl p-5">
                    <div className="flex items-center gap-2 mb-3">
                      <XCircle className="w-4 h-4 text-red-400" />
                      <h4 className="font-semibold text-white text-sm">Missing Skills</h4>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {result.missing_skills.map((s) => (
                        <SkillChip key={s} skill={s} variant="missing" animate />
                      ))}
                    </div>
                  </div>
                )}

                {/* AI Recommendations */}
                {result.recommendations.length > 0 && (
                  <AIInsightCard
                    title="AI Recommendations"
                    insights={result.recommendations.slice(0, 4)}
                  />
                )}
              </motion.div>
            ) : (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="bg-[#111114] border border-white/[0.08] rounded-2xl p-10 flex flex-col items-center text-center gap-4"
              >
                <div className="w-16 h-16 rounded-full bg-purple-500/10 flex items-center justify-center">
                  <GitCompare className="w-7 h-7 text-purple-400" />
                </div>
                <div>
                  <p className="font-display font-semibold text-white">Paste a JD and analyze</p>
                  <p className="text-[#A1A1AA] text-sm mt-1">
                    Results will appear here with match score, skill gaps, and AI tips
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
