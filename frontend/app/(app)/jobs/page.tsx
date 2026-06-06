"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  Briefcase, MapPin, Sparkles, Search, AlertCircle, Loader2, TrendingUp
} from "lucide-react";
import { useResume } from "@/context/ResumeContext";
import { useJobRecommendations } from "@/hooks/useJobRecommendations";
import JobCard from "@/components/ui/JobCard";
import AnalyticsCard from "@/components/ui/AnalyticsCard";
import GradientButton from "@/components/ui/GradientButton";
import { JobCardSkeleton } from "@/components/ui/LoadingSkeleton";

export default function JobsPage() {
  const { resumeId, resumeSkills } = useResume();
  const { fetch, data, loading, error, statusMessage } = useJobRecommendations();
  const [query, setQuery] = useState("machine learning engineer");
  const [location, setLocation] = useState("");
  const [topN, setTopN] = useState(10);

  const handleFetch = () => {
    if (!resumeId) return;
    fetch(resumeId, query, location, topN, resumeSkills.length ? resumeSkills : undefined);
  };

  const avgMatch = data?.jobs.length
    ? Math.round(data.jobs.reduce((s, j) => s + j.match_score, 0) / data.jobs.length)
    : 0;

  const topMatch = data?.jobs[0]?.match_score ?? 0;
  const locations = data?.jobs
    ? [...new Set(data.jobs.map((j) => j.location).filter(Boolean))].length
    : 0;

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-6">
        <div className="flex items-center gap-2 text-purple-400 text-sm font-medium mb-2">
          <Briefcase className="w-4 h-4" />
          Job Recommendations
        </div>
        <h1 className="font-display font-bold text-3xl text-white">Live Job Matches</h1>
        <p className="text-[#A1A1AA] text-sm mt-1.5">
          Real-time jobs from Adzuna API, scored against your resume via semantic matching.
        </p>
      </motion.div>

      {/* No resume warning */}
      {!resumeId && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mb-6 flex items-center gap-3 bg-yellow-500/5 border border-yellow-500/20 rounded-2xl p-4 text-yellow-400 text-sm"
        >
          <AlertCircle className="w-4 h-4 shrink-0" />
          Upload your resume first to get personalized job recommendations.
        </motion.div>
      )}

      {/* Search Controls */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-[#111114] border border-white/[0.08] rounded-2xl p-5 mb-6"
      >
        <div className="grid sm:grid-cols-3 gap-4">
          <div className="sm:col-span-1">
            <label className="text-xs text-[#A1A1AA] font-medium mb-1.5 block">Job Query</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#A1A1AA]" />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="machine learning engineer"
                className="w-full bg-[#18181C] border border-white/[0.08] rounded-xl pl-9 pr-3 py-2.5 text-sm text-white placeholder-[#A1A1AA] outline-none focus:border-purple-500/40 transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="text-xs text-[#A1A1AA] font-medium mb-1.5 block">Location</label>
            <div className="relative">
              <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#A1A1AA]" />
              <input
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="Any location"
                className="w-full bg-[#18181C] border border-white/[0.08] rounded-xl pl-9 pr-3 py-2.5 text-sm text-white placeholder-[#A1A1AA] outline-none focus:border-purple-500/40 transition-colors"
              />
            </div>
          </div>

          <div className="flex items-end">
            <GradientButton
              onClick={handleFetch}
              disabled={!resumeId || loading}
              loading={loading}
              className="w-full"
            >
              <Sparkles className="w-4 h-4" />
              {loading ? statusMessage || "Fetching..." : "Find Jobs"}
            </GradientButton>
          </div>
        </div>
      </motion.div>

      {/* Analytics row */}
      {data && !loading && (
        <div className="grid grid-cols-3 gap-4 mb-6">
          <AnalyticsCard
            label="Top Match"
            value={`${Math.round(topMatch)}%`}
            icon={<TrendingUp className="w-4 h-4" />}
            color="green"
            delay={0}
          />
          <AnalyticsCard
            label="Avg Match"
            value={`${avgMatch}%`}
            icon={<Sparkles className="w-4 h-4" />}
            color="purple"
            delay={0.05}
          />
          <AnalyticsCard
            label="Locations"
            value={locations}
            icon={<MapPin className="w-4 h-4" />}
            color="blue"
            delay={0.1}
          />
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mb-6 flex items-center gap-3 bg-red-500/5 border border-red-500/20 rounded-2xl p-4 text-red-400 text-sm">
          <AlertCircle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      {/* Loading skeletons */}
      {loading && (
        <div className="space-y-3">
          <div className="flex items-center gap-3 text-[#A1A1AA] text-sm mb-4">
            <Loader2 className="w-4 h-4 animate-spin text-purple-400" />
            {statusMessage || "Processing..."}
          </div>
          <div className="grid lg:grid-cols-2 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <JobCardSkeleton key={i} />
            ))}
          </div>
        </div>
      )}

      {/* Jobs Grid */}
      {data && !loading && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-display font-semibold text-white">
              {data.total_jobs} Matches Found
            </h3>
            <span className="text-xs text-[#A1A1AA]">Ranked by semantic match score</span>
          </div>
          {data.jobs.length === 0 ? (
            <div className="text-center py-16 text-[#A1A1AA]">
              <Briefcase className="w-10 h-10 mx-auto mb-3 opacity-40" />
              <p>No jobs found. Try a different search query.</p>
            </div>
          ) : (
            <div className="grid lg:grid-cols-2 gap-4">
              {data.jobs.map((job, i) => (
                <JobCard key={i} job={job} index={i} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Empty state */}
      {!data && !loading && !error && resumeId && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-20"
        >
          <Briefcase className="w-12 h-12 text-[#A1A1AA] mx-auto mb-4 opacity-40" />
          <p className="font-display font-semibold text-white mb-2">Ready to find your matches</p>
          <p className="text-[#A1A1AA] text-sm">
            Enter a job query and click <span className="text-purple-400">Find Jobs</span>
          </p>
        </motion.div>
      )}
    </div>
  );
}
