"use client";

import { motion } from "framer-motion";
import { scoreColor } from "@/lib/utils";

interface MatchRingProps {
  score: number;
  size?: number;
  strokeWidth?: number;
  label?: string;
}

export default function MatchRing({
  score,
  size = 120,
  strokeWidth = 8,
  label,
}: MatchRingProps) {
  const radius = (size - strokeWidth * 2) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color = scoreColor(score);
  const center = size / 2;

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: size, height: size }}>
        <svg
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
          className="-rotate-90"
        >
          <defs>
            <linearGradient id={`ring-grad-${score}`} x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor={color} stopOpacity="0.8" />
              <stop offset="100%" stopColor={color} />
            </linearGradient>
          </defs>
          {/* Track */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="rgba(255,255,255,0.06)"
            strokeWidth={strokeWidth}
          />
          {/* Progress */}
          <motion.circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke={`url(#ring-grad-${score})`}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.2, ease: "easeOut" }}
            style={{
              filter: `drop-shadow(0 0 6px ${color}80)`,
            }}
          />
        </svg>

        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="font-display font-bold text-white leading-none"
            style={{ fontSize: size * 0.22 }}
          >
            {Math.round(score)}
          </motion.span>
          <span
            className="text-[#A1A1AA] font-medium leading-none mt-0.5"
            style={{ fontSize: size * 0.1 }}
          >
            %
          </span>
        </div>
      </div>

      {label && (
        <span className="text-xs text-[#A1A1AA] font-medium">{label}</span>
      )}
    </div>
  );
}
