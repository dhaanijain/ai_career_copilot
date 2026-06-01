"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  FileText,
  Briefcase,
  TrendingUp,
  GitCompare,
  Settings,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/context/AuthContext";

const NAV_ITEMS = [
  { href: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/resume", icon: FileText, label: "Resume Analysis" },
  { href: "/jobs", icon: Briefcase, label: "Job Recommendations" },
  { href: "/skill-gap", icon: TrendingUp, label: "Skill Gap" },
  { href: "/jd-match", icon: GitCompare, label: "JD Match" },
  { href: "/settings", icon: Settings, label: "Settings" },
];

function getInitials(name?: string | null, email?: string | null): string {
  if (name && name.trim()) {
    return name
      .trim()
      .split(/\s+/)
      .slice(0, 2)
      .map((w) => w[0])
      .join("")
      .toUpperCase();
  }
  if (email) return email[0].toUpperCase();
  return "?";
}

export default function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuth();

  const displayName =
    user?.user_metadata?.full_name || user?.email?.split("@")[0] || "User";
  const email = user?.email ?? "";
  const initials = getInitials(user?.user_metadata?.full_name, user?.email);

  return (
    <aside className="hidden md:flex flex-col w-60 shrink-0 bg-[#0D0D10] border-r border-white/[0.06] h-full">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-5 h-16 border-b border-white/[0.06]">
        <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-purple-600 to-purple-400 flex items-center justify-center shadow-[0_0_16px_rgba(139,92,246,0.5)]">
          <Sparkles className="w-4 h-4 text-white" />
        </div>
        <span className="font-display font-semibold text-[15px] text-white tracking-tight">
          Career Copilot
        </span>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {NAV_ITEMS.map((item) => {
          const active =
            pathname === item.href || pathname.startsWith(item.href + "/");
          const Icon = item.icon;
          return (
            <Link key={item.href} href={item.href}>
              <motion.div
                whileHover={{ x: 2 }}
                className={cn(
                  "relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors duration-150 cursor-pointer group",
                  active
                    ? "text-white"
                    : "text-[#A1A1AA] hover:text-white hover:bg-white/[0.04]"
                )}
              >
                {active && (
                  <motion.div
                    layoutId="sidebar-active"
                    className="absolute inset-0 rounded-xl bg-gradient-to-r from-purple-600/20 to-purple-400/10 border border-purple-500/20"
                    transition={{ type: "spring", bounce: 0.2, duration: 0.4 }}
                  />
                )}
                <Icon
                  className={cn(
                    "w-4 h-4 relative z-10 transition-colors",
                    active
                      ? "text-purple-400"
                      : "text-[#A1A1AA] group-hover:text-white"
                  )}
                />
                <span className="relative z-10">{item.label}</span>
                {active && (
                  <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-full bg-purple-500" />
                )}
              </motion.div>
            </Link>
          );
        })}
      </nav>

      {/* User info + CTA */}
      <div className="px-3 pb-5 space-y-3">
        {/* User profile card */}
        <div className="flex items-center gap-2.5 px-3 py-2.5 rounded-xl bg-white/[0.03] border border-white/[0.06]">
          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-purple-600 to-blue-accent flex items-center justify-center text-white text-[11px] font-semibold shrink-0 select-none">
            {initials}
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-xs font-medium text-white truncate leading-tight">
              {displayName}
            </p>
            <p className="text-[11px] text-[#A1A1AA] truncate leading-tight mt-0.5">
              {email}
            </p>
          </div>
        </div>

        {/* CTA */}
        <Link href="/resume">
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-purple-500 text-white text-sm font-semibold shadow-[0_0_20px_rgba(139,92,246,0.3)] hover:shadow-[0_0_28px_rgba(139,92,246,0.45)] transition-shadow duration-300 cursor-pointer"
          >
            <Sparkles className="w-4 h-4" />
            Analyze New Resume
          </motion.div>
        </Link>
      </div>
    </aside>
  );
}
