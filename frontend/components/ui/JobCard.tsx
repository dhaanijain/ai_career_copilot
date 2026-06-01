"use client";

import { motion } from "framer-motion";
import { MapPin, ExternalLink, CheckCircle2, XCircle, Zap } from "lucide-react";
import MatchRing from "./MatchRing";
import SkillChip from "./SkillChip";
import { JobRecommendation } from "@/types";
import { truncate } from "@/lib/utils";

interface JobCardProps {
  job: JobRecommendation;
  index: number;
}

export default function JobCard({ job, index }: JobCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06, duration: 0.4 }}
      whileHover={{ y: -2 }}
      className="group relative bg-[#111114] border border-white/[0.08] rounded-2xl p-5 hover:border-purple-500/30 hover:shadow-[0_0_30px_rgba(139,92,246,0.12)] transition-all duration-300"
    >
      {/* Rank badge */}
      <div className="absolute top-4 right-4">
        <span className="text-[10px] font-bold text-[#A1A1AA] bg-white/[0.06] px-2 py-0.5 rounded-full">
          #{index + 1}
        </span>
      </div>

      <div className="flex gap-4">
        {/* Match Ring */}
        <div className="shrink-0">
          <MatchRing score={job.match_score} size={80} strokeWidth={6} />
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <h3 className="font-display font-semibold text-white text-[15px] leading-tight truncate pr-8">
            {job.title}
          </h3>
          <p className="text-[#A1A1AA] text-sm mt-0.5">{job.company || "Company"}</p>
          {job.location && (
            <div className="flex items-center gap-1 mt-1">
              <MapPin className="w-3 h-3 text-[#A1A1AA]" />
              <span className="text-xs text-[#A1A1AA]">{job.location}</span>
            </div>
          )}
        </div>
      </div>

      {/* Skills */}
      <div className="mt-4 space-y-2.5">
        {job.matching_skills.length > 0 && (
          <div>
            <div className="flex items-center gap-1.5 mb-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider">
                Matched
              </span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {job.matching_skills.slice(0, 4).map((s) => (
                <SkillChip key={s} skill={s} variant="match" size="sm" />
              ))}
              {job.matching_skills.length > 4 && (
                <span className="text-[11px] text-[#A1A1AA] self-center">
                  +{job.matching_skills.length - 4} more
                </span>
              )}
            </div>
          </div>
        )}

        {job.missing_skills.length > 0 && (
          <div>
            <div className="flex items-center gap-1.5 mb-1.5">
              <XCircle className="w-3.5 h-3.5 text-red-400" />
              <span className="text-[11px] font-semibold text-red-400 uppercase tracking-wider">
                Gaps
              </span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {job.missing_skills.slice(0, 3).map((s) => (
                <SkillChip key={s} skill={s} variant="missing" size="sm" />
              ))}
              {job.missing_skills.length > 3 && (
                <span className="text-[11px] text-[#A1A1AA] self-center">
                  +{job.missing_skills.length - 3} more
                </span>
              )}
            </div>
          </div>
        )}

        {job.recommendations.length > 0 && (
          <div className="bg-purple-500/5 border border-purple-500/10 rounded-xl px-3 py-2">
            <div className="flex items-center gap-1.5 mb-1">
              <Zap className="w-3 h-3 text-purple-400" />
              <span className="text-[11px] font-semibold text-purple-400 uppercase tracking-wider">
                AI Tip
              </span>
            </div>
            <p className="text-[12px] text-[#A1A1AA] leading-relaxed">
              {truncate(job.recommendations[0], 110)}
            </p>
          </div>
        )}
      </div>

      {/* Apply */}
      {job.redirect_url && (
        <div className="mt-4 pt-4 border-t border-white/[0.06]">
          <a
            href={job.redirect_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-purple-400 hover:text-purple-300 transition-colors"
          >
            Apply Now
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      )}
    </motion.div>
  );
}
