"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { ReactNode } from "react";
import { ArrowRight } from "lucide-react";

interface DashboardCardProps {
  title: string;
  description: string;
  icon: ReactNode;
  href: string;
  gradient?: string;
  delay?: number;
}

export default function DashboardCard({
  title,
  description,
  icon,
  href,
  gradient = "from-purple-600/20 to-purple-400/5",
  delay = 0,
}: DashboardCardProps) {
  return (
    <Link href={href}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay, duration: 0.4 }}
        whileHover={{ y: -3 }}
        className={`group relative bg-gradient-to-br ${gradient} border border-white/[0.08] rounded-2xl p-6 cursor-pointer hover:border-purple-500/20 hover:shadow-[0_0_30px_rgba(139,92,246,0.1)] transition-all duration-300 overflow-hidden`}
      >
        {/* Background shimmer on hover */}
        <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none">
          <div className="absolute inset-0 bg-gradient-to-br from-purple-600/5 to-transparent rounded-2xl" />
        </div>

        <div className="flex items-start justify-between">
          <div className="w-10 h-10 rounded-xl bg-white/[0.06] border border-white/[0.08] flex items-center justify-center">
            {icon}
          </div>
          <ArrowRight className="w-4 h-4 text-[#A1A1AA] group-hover:text-purple-400 group-hover:translate-x-1 transition-all duration-200" />
        </div>

        <div className="mt-4">
          <h3 className="font-display font-semibold text-white text-[15px]">{title}</h3>
          <p className="text-[#A1A1AA] text-sm mt-1.5 leading-relaxed">{description}</p>
        </div>
      </motion.div>
    </Link>
  );
}
