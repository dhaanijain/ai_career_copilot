"use client";

import { useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  TrendingUp, AlertCircle, Sparkles, XCircle, CheckCircle2, ArrowRight
} from "lucide-react";
import { useResume } from "@/context/ResumeContext";
import { useSkillGap } from "@/hooks/useSkillGap";
import MatchRing from "@/components/ui/MatchRing";
import SkillChip from "@/components/ui/SkillChip";
import AIInsightCard from "@/components/ui/AIInsightCard";
import GradientButton from "@/components/ui/GradientButton";
import AnalyticsCard from "@/components/ui/AnalyticsCard";
import { SkillsSkeleton } from "@/components/ui/LoadingSkeleton";
import { scoreColor } from "@/lib/utils";

export default function SkillGapPage() {
  const { resumeId, resumeSkills } = useResume();
  const { analyze, data, loading, error } = useSkillGap();

  useEffect(() => {
    if (resumeId && !data && !loading) {
      analyze(resumeId);
    }
  }, [resumeId]);

  const coverageScore = data
    ? Math.round((data.resume_skills.length / (data.resume_skills.length + data.missing_skills.length)) * 100)
    : 0;

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
        <div className="flex items-center gap-2 text-purple-400 text-sm font-medium mb-2">
          <TrendingUp className="w-4 h-4" />
          Skill Gap
        </div>
        <h1 className="font-display font-bold text-3xl text-white">Skill Gap Analysis</h1>
        <p className="text-[#A1A1AA] text-sm mt-1.5">
          Your skills benchmarked against modern ML/AI engineering standards.
        </p>
      </motion.div>

      {!resumeId && (
        <div className="mb-6 flex items-center gap-3 bg-yellow-500/5 border border-yellow-500/20 rounded-2xl p-4 text-yellow-400 text-sm">
          <AlertCircle className="w-4 h-4 shrink-0" />
          Upload your resume to run skill gap analysis.
        </div>
      )}

      {resumeId && !data && !loading && (
        <div className="flex justify-center mb-6">
          <GradientButton onClick={() => analyze(resumeId)}>
            <Sparkles className="w-4 h-4" />
            Analyze Skill Gap
          </GradientButton>
        </div>
      )}

      {error && (
        <div className="mb-6 flex items-center gap-3 bg-red-500/5 border border-red-500/20 rounded-2xl p-4 text-red-400 text-sm">
          <AlertCircle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      {loading && (
        <div className="space-y-4">
          <SkillsSkeleton />
        </div>
      )}

      <AnimatePresence>
        {data && !loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
          >
            {/* Analytics row */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <AnalyticsCard
                label="Market Coverage"
                value={`${data.match_score.toFixed(0)}%`}
                icon={<TrendingUp className="w-4 h-4" />}
                color="purple"
                delay={0}
              />
              <AnalyticsCard
                label="Skills You Have"
                value={data.resume_skills.length}
                icon={<CheckCircle2 className="w-4 h-4" />}
                color="green"
                delay={0.05}
              />
              <AnalyticsCard
                label="Skill Gaps"
                value={data.missing_skills.length}
                icon={<XCircle className="w-4 h-4" />}
                color="red"
                delay={0.1}
              />
              <AnalyticsCard
                label="Semantic Gaps"
                value={data.semantic_gaps.length}
                icon={<ArrowRight className="w-4 h-4" />}
                color="blue"
                delay={0.15}
              />
            </div>

            <div className="grid lg:grid-cols-3 gap-6">
              {/* Score + Missing */}
              <div className="space-y-4">
                {/* Match ring */}
                <div className="bg-[#111114] border border-white/[0.08] rounded-2xl p-6 flex flex-col items-center gap-3">
                  <MatchRing score={data.match_score} size={140} strokeWidth={10} label="Market Coverage Score" />
                  <p className="text-xs text-[#A1A1AA] text-center max-w-[180px]">
                    vs modern ML/AI engineering skill requirements
                  </p>
                </div>

                {/* Missing skill competency bars */}
                {data.missing_skills.length > 0 && (
                  <div className="bg-[#111114] border border-white/[0.08] rounded-2xl p-5">
                    <div className="flex items-center gap-2 mb-4">
                      <XCircle className="w-4 h-4 text-red-400" />
                      <h4 className="font-semibold text-white text-sm">Skill Gaps</h4>
                    </div>
                    <div className="space-y-3">
                      {data.missing_skills.slice(0, 8).map((skill, i) => {
                        const barWidth = Math.max(10, 100 - i * 8);
                        return (
                          <div key={skill}>
                            <div className="flex justify-between text-xs mb-1">
                              <span className="text-[#A1A1AA]">{skill}</span>
                              <span className="text-red-400">Gap</span>
                            </div>
                            <div className="h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
                              <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${barWidth}%` }}
                                transition={{ delay: i * 0.05, duration: 0.6, ease: "easeOut" }}
                                className="h-full rounded-full bg-gradient-to-r from-red-500/60 to-red-400/40"
                              />
                            </div>
                          </div>
                        );
                      })}
                      {data.missing_skills.length > 8 && (
                        <p className="text-xs text-[#A1A1AA] text-center pt-1">
                          +{data.missing_skills.length - 8} more gaps
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Skills you have + semantic gaps */}
              <div className="space-y-4">
                <div className="bg-[#111114] border border-white/[0.08] rounded-2xl p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <h4 className="font-semibold text-white text-sm">Your Skills</h4>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {data.resume_skills.map((s) => (
                      <SkillChip key={s} skill={s} variant="match" size="sm" animate />
                    ))}
                  </div>
                </div>

                {data.semantic_gaps.length > 0 && (
                  <div className="bg-[#111114] border border-white/[0.08] rounded-2xl p-5">
                    <div className="flex items-center gap-2 mb-3">
                      <ArrowRight className="w-4 h-4 text-blue-400" />
                      <h4 className="font-semibold text-white text-sm">Close Matches</h4>
                      <span className="text-xs text-[#A1A1AA]">(semantic gaps)</span>
                    </div>
                    <div className="space-y-2">
                      {data.semantic_gaps.slice(0, 5).map((sg, i) => (
                        <div key={i} className="flex items-center justify-between text-xs">
                          <div className="flex items-center gap-2">
                            <SkillChip skill={sg.resume_skill} variant="neutral" size="sm" />
                            <span className="text-[#A1A1AA]">≈</span>
                            <SkillChip skill={sg.jd_skill} variant="semantic" size="sm" />
                          </div>
                          <span className="text-[#A1A1AA]">
                            {Math.round(sg.similarity * 100)}%
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Recommendations */}
              <div className="space-y-4">
                {data.recommendations.length > 0 && (
                  <AIInsightCard
                    title="AI Learning Roadmap"
                    insights={data.recommendations.slice(0, 5)}
                  />
                )}

                {Object.keys(data.category_tips).length > 0 && (
                  <div className="bg-[#111114] border border-white/[0.08] rounded-2xl p-5">
                    <div className="flex items-center gap-2 mb-3">
                      <Sparkles className="w-4 h-4 text-purple-400" />
                      <h4 className="font-semibold text-white text-sm">Category Guidance</h4>
                    </div>
                    <div className="space-y-3">
                      {Object.entries(data.category_tips).map(([cat, tip]) => (
                        <div key={cat} className="border-l-2 border-purple-500/30 pl-3">
                          <p className="text-xs font-semibold text-purple-400 uppercase tracking-wide mb-0.5">
                            {cat}
                          </p>
                          <p className="text-xs text-[#A1A1AA] leading-relaxed">{tip}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <GradientButton
                  onClick={() => resumeId && analyze(resumeId)}
                  variant="outline"
                  className="w-full"
                >
                  Re-analyze
                </GradientButton>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
