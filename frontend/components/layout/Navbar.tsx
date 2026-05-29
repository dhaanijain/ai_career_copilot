"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Sparkles, User, ChevronRight } from "lucide-react";

const BREADCRUMBS: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/resume": "Resume Analysis",
  "/jobs": "Job Recommendations",
  "/skill-gap": "Skill Gap",
  "/jd-match": "JD Match",
  "/settings": "Settings",
};

export default function Navbar() {
  const pathname = usePathname();
  const label = BREADCRUMBS[pathname] ?? "AI Career Copilot";

  return (
    <header className="h-14 shrink-0 border-b border-white/[0.06] flex items-center justify-between px-6 bg-[#07070A]/80 backdrop-blur-sm">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm">
        <span className="text-[#A1A1AA]">Copilot</span>
        <ChevronRight className="w-3.5 h-3.5 text-[#A1A1AA]" />
        <span className="text-white font-medium">{label}</span>
      </div>

      {/* Profile */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-600 to-blue-accent flex items-center justify-center text-white text-xs font-semibold">
          DJ
        </div>
      </div>
    </header>
  );
}
