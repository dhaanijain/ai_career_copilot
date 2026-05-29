"use client";

import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";

interface AIInsightCardProps {
  title: string;
  insights: string[];
  delay?: number;
}

export default function AIInsightCard({ title, insights, delay = 0 }: AIInsightCardProps) {
  if (!insights.length) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
      className="bg-gradient-to-br from-purple-600/10 to-blue-600/5 border border-purple-500/15 rounded-2xl p-5"
    >
      <div className="flex items-center gap-2 mb-3">
        <div className="w-6 h-6 rounded-lg bg-purple-500/20 flex items-center justify-center">
          <Sparkles className="w-3.5 h-3.5 text-purple-400" />
        </div>
        <h4 className="font-display font-semibold text-sm text-white">{title}</h4>
      </div>
      <ul className="space-y-2">
        {insights.map((insight, i) => (
          <li key={i} className="flex items-start gap-2 text-sm text-[#A1A1AA] leading-relaxed">
            <span className="w-1.5 h-1.5 rounded-full bg-purple-500 shrink-0 mt-1.5" />
            {insight}
          </li>
        ))}
      </ul>
    </motion.div>
  );
}
