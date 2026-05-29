"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";

interface AnalyticsCardProps {
  label: string;
  value: string | number;
  sub?: string;
  icon: ReactNode;
  color?: "purple" | "blue" | "green" | "red";
  delay?: number;
}

const COLOR_MAP = {
  purple: {
    icon: "bg-purple-500/10 text-purple-400",
    value: "text-purple-300",
    glow: "hover:shadow-[0_0_24px_rgba(139,92,246,0.12)]",
  },
  blue: {
    icon: "bg-blue-500/10 text-blue-400",
    value: "text-blue-300",
    glow: "hover:shadow-[0_0_24px_rgba(56,189,248,0.12)]",
  },
  green: {
    icon: "bg-emerald-500/10 text-emerald-400",
    value: "text-emerald-300",
    glow: "hover:shadow-[0_0_24px_rgba(34,197,94,0.12)]",
  },
  red: {
    icon: "bg-red-500/10 text-red-400",
    value: "text-red-300",
    glow: "hover:shadow-[0_0_24px_rgba(239,68,68,0.12)]",
  },
};

export default function AnalyticsCard({
  label,
  value,
  sub,
  icon,
  color = "purple",
  delay = 0,
}: AnalyticsCardProps) {
  const c = COLOR_MAP[color];

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
      className={`bg-[#111114] border border-white/[0.08] rounded-2xl p-5 flex items-center gap-4 transition-shadow duration-300 ${c.glow}`}
    >
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${c.icon}`}>
        {icon}
      </div>
      <div>
        <p className="text-[#A1A1AA] text-xs font-medium tracking-wide uppercase">{label}</p>
        <p className={`font-display font-bold text-2xl mt-0.5 ${c.value}`}>{value}</p>
        {sub && <p className="text-[#A1A1AA] text-xs mt-0.5">{sub}</p>}
      </div>
    </motion.div>
  );
}
