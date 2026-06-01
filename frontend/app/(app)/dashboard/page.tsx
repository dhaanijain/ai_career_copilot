"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { FileText, Briefcase, TrendingUp, GitCompare, Sparkles, Brain, CheckCircle2 } from "lucide-react";
import { useResume } from "@/context/ResumeContext";
import DashboardCard from "@/components/ui/DashboardCard";
import SkillChip from "@/components/ui/SkillChip";
import GradientButton from "@/components/ui/GradientButton";

const CARDS = [
  {
    title: "Resume Analysis",
    description: "Upload your PDF resume and let AI extract every technical skill with confidence scoring.",
    icon: <FileText className="w-5 h-5 text-purple-400" />,
    href: "/resume",
    gradient: "from-purple-600/15 to-purple-400/5",
    delay: 0.1,
  },
  {
    title: "Job Recommendations",
    description: "Get live job listings ranked by semantic match score against your resume.",
    icon: <Briefcase className="w-5 h-5 text-blue-400" />,
    href: "/jobs",
    gradient: "from-blue-600/15 to-blue-400/5",
    delay: 0.2,
  },
  {
    title: "Skill Gap Analysis",
    description: "Identify missing skills against modern tech standards and get a learning roadmap.",
    icon: <TrendingUp className="w-5 h-5 text-emerald-400" />,
    href: "/skill-gap",
    gradient: "from-emerald-600/15 to-emerald-400/5",
    delay: 0.3,
  },
  {
    title: "JD Match",
    description: "Paste any job description to get an instant AI match score with semantic analysis.",
    icon: <GitCompare className="w-5 h-5 text-purple-400" />,
    href: "/jd-match",
    gradient: "from-purple-600/15 to-blue-400/5",
    delay: 0.4,
  },
];

export default function DashboardPage() {
  const { resumeId, resumeSkills, fileName } = useResume();

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-2 text-purple-400 text-sm font-medium mb-2">
          <Sparkles className="w-4 h-4" />
          AI Career Copilot
        </div>
        <h1 className="font-display font-bold text-3xl text-white">Dashboard</h1>
        <p className="text-[#A1A1AA] text-sm mt-1.5">
          {resumeId
            ? `Resume loaded · ${resumeSkills.length} skills detected`
            : "Upload your resume to get started"}
        </p>
      </motion.div>

      {/* Resume Status Banner */}
      {resumeId ? (
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          className="mb-8 bg-gradient-to-r from-emerald-600/10 to-emerald-400/5 border border-emerald-500/20 rounded-2xl p-5 flex items-center justify-between"
        >
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            </div>
            <div>
              <p className="text-white font-semibold text-sm">Resume Active</p>
              <p className="text-[#A1A1AA] text-xs mt-0.5">
                {fileName || "resume.pdf"} · {resumeSkills.length} skills extracted
              </p>
            </div>
          </div>
          <Link href="/resume">
            <GradientButton variant="outline" size="sm">Change Resume</GradientButton>
          </Link>
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          className="mb-8 bg-gradient-to-r from-purple-600/10 to-purple-400/5 border border-purple-500/20 rounded-2xl p-6 text-center"
        >
          <Brain className="w-8 h-8 text-purple-400 mx-auto mb-3" />
          <h3 className="font-display font-semibold text-white mb-1">No Resume Uploaded</h3>
          <p className="text-[#A1A1AA] text-sm mb-4">
            Upload your resume to unlock all AI features
          </p>
          <Link href="/resume">
            <GradientButton>
              <FileText className="w-4 h-4" />
              Upload Resume
            </GradientButton>
          </Link>
        </motion.div>
      )}

      {/* Feature Cards */}
      <div className="grid sm:grid-cols-2 gap-4 mb-8">
        {CARDS.map((card) => (
          <DashboardCard key={card.href} {...card} />
        ))}
      </div>

      {/* Skills Preview */}
      {resumeSkills.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-[#111114] border border-white/[0.08] rounded-2xl p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-display font-semibold text-white">Extracted Skills</h3>
            <span className="text-xs text-[#A1A1AA] bg-white/[0.06] px-2.5 py-1 rounded-full">
              {resumeSkills.length} total
            </span>
          </div>
          <div className="flex flex-wrap gap-2">
            {resumeSkills.map((skill) => (
              <SkillChip key={skill} skill={skill} variant="neutral" animate />
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}
