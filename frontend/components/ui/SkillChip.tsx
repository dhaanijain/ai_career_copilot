"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface SkillChipProps {
  skill: string;
  variant?: "match" | "missing" | "neutral" | "semantic";
  size?: "sm" | "md";
  animate?: boolean;
}

const VARIANTS = {
  match: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  missing: "bg-red-500/10 text-red-400 border-red-500/20",
  semantic: "bg-blue-500/10 text-blue-300 border-blue-500/20",
  neutral: "bg-white/[0.06] text-[#A1A1AA] border-white/[0.08]",
};

export default function SkillChip({
  skill,
  variant = "neutral",
  size = "md",
  animate = false,
}: SkillChipProps) {
  const chip = (
    <span
      className={cn(
        "inline-flex items-center rounded-lg border font-medium tracking-wide transition-colors",
        size === "sm" ? "px-2 py-0.5 text-[11px]" : "px-2.5 py-1 text-xs",
        VARIANTS[variant]
      )}
    >
      {skill}
    </span>
  );

  if (animate) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.85 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.2 }}
        className="inline-block"
      >
        {chip}
      </motion.div>
    );
  }

  return chip;
}
