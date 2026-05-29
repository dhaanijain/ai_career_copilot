"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import {
  Sparkles,
  FileText,
  Briefcase,
  TrendingUp,
  GitCompare,
  Brain,
  ArrowRight,
  Zap,
  Shield,
  Cpu,
} from "lucide-react";
import GradientButton from "@/components/ui/GradientButton";

const FEATURES = [
  {
    icon: <Brain className="w-5 h-5" />,
    title: "AI Resume Parsing",
    description: "Advanced OCR + NLP pipeline extracts every technical skill from your PDF with confidence scoring.",
    color: "purple",
  },
  {
    icon: <GitCompare className="w-5 h-5" />,
    title: "Semantic JD Matching",
    description: "Two-pass exact + cosine similarity matching scores your resume against any job description.",
    color: "blue",
  },
  {
    icon: <Briefcase className="w-5 h-5" />,
    title: "Live Job Recommendations",
    description: "Fetches real jobs from Adzuna API and ranks them by your semantic match score.",
    color: "green",
  },
  {
    icon: <TrendingUp className="w-5 h-5" />,
    title: "Skill Gap Analysis",
    description: "Identifies missing skills against modern tech standards and generates AI-driven learning roadmaps.",
    color: "purple",
  },
  {
    icon: <Zap className="w-5 h-5" />,
    title: "Career Intelligence",
    description: "Actionable per-skill recommendations, category tips, and visibility alerts for your resume.",
    color: "blue",
  },
];

const COLOR_MAP: Record<string, string> = {
  purple: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  blue: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  green: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
};

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#07070A] relative overflow-hidden">
      {/* Ambient background */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] rounded-full bg-purple-600/8 blur-[120px]" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] rounded-full bg-blue-500/6 blur-[120px]" />
        <div className="absolute top-1/3 right-0 w-[400px] h-[400px] rounded-full bg-purple-800/5 blur-[100px]" />
      </div>

      {/* Navbar */}
      <nav className="relative z-10 flex items-center justify-between px-8 h-16 border-b border-white/[0.06]">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-purple-600 to-purple-400 flex items-center justify-center shadow-[0_0_16px_rgba(139,92,246,0.5)]">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <span className="font-display font-semibold text-white tracking-tight">Career Copilot</span>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/dashboard">
            <GradientButton variant="outline" size="sm">Dashboard</GradientButton>
          </Link>
          <Link href="/resume">
            <GradientButton size="sm">Upload Resume</GradientButton>
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative z-10 max-w-7xl mx-auto px-8 pt-24 pb-20">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Left */}
          <div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 text-xs font-semibold mb-6">
                <Cpu className="w-3.5 h-3.5" />
                AI-Powered Career Intelligence
              </div>

              <h1 className="font-display font-bold text-5xl lg:text-6xl text-white leading-[1.1] tracking-tight">
                Your AI-Powered
                <br />
                <span className="bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                  Career Copilot
                </span>
              </h1>

              <p className="text-[#A1A1AA] text-lg mt-6 leading-relaxed max-w-lg">
                Upload your resume, discover matching jobs, analyze skill gaps, and receive
                intelligent AI-powered career recommendations — all in one platform.
              </p>

              <div className="flex items-center gap-4 mt-8">
                <Link href="/resume">
                  <GradientButton size="lg">
                    <FileText className="w-4 h-4" />
                    Upload Resume
                  </GradientButton>
                </Link>
                <Link href="/jobs">
                  <GradientButton variant="secondary" size="lg">
                    Explore Jobs
                    <ArrowRight className="w-4 h-4" />
                  </GradientButton>
                </Link>
              </div>

              <div className="flex items-center gap-6 mt-10">
                {[
                  { icon: <Shield className="w-4 h-4 text-emerald-400" />, label: "Semantic AI Matching" },
                  { icon: <Zap className="w-4 h-4 text-purple-400" />, label: "Live Job Feed" },
                  { icon: <Brain className="w-4 h-4 text-blue-400" />, label: "Skill Intelligence" },
                ].map((item) => (
                  <div key={item.label} className="flex items-center gap-1.5 text-xs text-[#A1A1AA]">
                    {item.icon}
                    {item.label}
                  </div>
                ))}
              </div>
            </motion.div>
          </div>

          {/* Right — floating glassmorphism panels */}
          <div className="hidden lg:block relative h-[480px]">
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.7, delay: 0.2 }}
              className="absolute top-8 right-0 w-72 glass rounded-2xl p-5 border border-white/[0.08]"
            >
              <div className="flex items-center gap-2 mb-3">
                <div className="w-2 h-2 rounded-full bg-emerald-400" />
                <span className="text-xs text-[#A1A1AA] font-medium">Resume Analyzed</span>
              </div>
              <div className="font-display font-bold text-4xl text-white">87<span className="text-lg text-purple-400">%</span></div>
              <div className="text-xs text-[#A1A1AA] mt-1">Match score · Senior ML Engineer</div>
              <div className="mt-3 flex flex-wrap gap-1.5">
                {["PyTorch", "Python", "FastAPI", "Docker"].map(s => (
                  <span key={s} className="text-[10px] font-medium px-2 py-0.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">{s}</span>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.7, delay: 0.4 }}
              className="absolute top-36 left-0 w-64 glass rounded-2xl p-4 border border-white/[0.08]"
            >
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-4 h-4 text-purple-400" />
                <span className="text-xs text-white font-semibold">Skill Gap</span>
              </div>
              <div className="space-y-2">
                {[["Kubernetes", 78], ["Terraform", 45], ["RAG", 60]].map(([skill, val]) => (
                  <div key={String(skill)}>
                    <div className="flex justify-between text-[10px] mb-0.5">
                      <span className="text-[#A1A1AA]">{skill}</span>
                      <span className="text-white font-medium">{val}%</span>
                    </div>
                    <div className="h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-purple-600 to-purple-400 rounded-full" style={{ width: `${val}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.5 }}
              className="absolute bottom-8 right-8 w-72 glass rounded-2xl p-4 border border-white/[0.08]"
            >
              <div className="flex items-center gap-2 mb-3">
                <Briefcase className="w-4 h-4 text-blue-400" />
                <span className="text-xs text-white font-semibold">Top Job Match</span>
              </div>
              <div className="text-sm font-display font-semibold text-white">AI/ML Engineer</div>
              <div className="text-xs text-[#A1A1AA] mt-0.5">Anthropic · San Francisco</div>
              <div className="flex items-center justify-between mt-3">
                <span className="text-xs text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full">92% match</span>
                <span className="text-xs text-[#A1A1AA]">3 skills gap</span>
              </div>
            </motion.div>

            {/* Glow orb */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 rounded-full bg-purple-600/10 blur-3xl pointer-events-none" />
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="relative z-10 max-w-7xl mx-auto px-8 pb-24">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="text-center mb-12"
        >
          <h2 className="font-display font-bold text-3xl text-white">
            Built for serious job seekers
          </h2>
          <p className="text-[#A1A1AA] mt-3 max-w-xl mx-auto">
            Every feature connects directly to the AI pipeline — no static data, no fake scores.
          </p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {FEATURES.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * i + 0.4 }}
              whileHover={{ y: -3 }}
              className="bg-[#111114] border border-white/[0.08] rounded-2xl p-6 hover:border-purple-500/20 hover:shadow-[0_0_24px_rgba(139,92,246,0.08)] transition-all duration-300 group"
            >
              <div className={`w-9 h-9 rounded-xl flex items-center justify-center border mb-4 ${COLOR_MAP[f.color]}`}>
                {f.icon}
              </div>
              <h3 className="font-display font-semibold text-white text-[15px] mb-2">{f.title}</h3>
              <p className="text-[#A1A1AA] text-sm leading-relaxed">{f.description}</p>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
}
