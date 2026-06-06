"use client";

import { usePathname } from "next/navigation";
import { ChevronRight, LogOut } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/context/ToastContext";

const BREADCRUMBS: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/resume": "Resume Analysis",
  "/jobs": "Job Recommendations",
  "/skill-gap": "Skill Gap",
  "/jd-match": "JD Match",
  "/settings": "Settings",
};

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

export default function Navbar() {
  const pathname = usePathname();
  const { user, signOut } = useAuth();
  const { toast } = useToast();
  const label = BREADCRUMBS[pathname] ?? "AI Career Copilot";

  const handleLogout = async () => {
    try {
      await signOut();
      toast("success", "Signed out successfully.");
      // Navigation is handled by AppLayout's useEffect which watches for user becoming null
    } catch {
      toast("error", "Failed to sign out. Please try again.");
    }
  };

  const initials = getInitials(
    user?.user_metadata?.full_name,
    user?.email
  );

  return (
    <header className="h-14 shrink-0 border-b border-white/[0.06] flex items-center justify-between px-6 bg-[#07070A]/80 backdrop-blur-sm">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm">
        <span className="text-[#A1A1AA]">Copilot</span>
        <ChevronRight className="w-3.5 h-3.5 text-[#A1A1AA]" />
        <span className="text-white font-medium">{label}</span>
      </div>

      {/* Profile + Logout */}
      <div className="flex items-center gap-3">
        {/* Avatar */}
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-600 to-blue-accent flex items-center justify-center text-white text-xs font-semibold select-none">
          {initials}
        </div>

        {/* Logout */}
        <button
          onClick={handleLogout}
          title="Sign out"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[#A1A1AA] hover:text-white hover:bg-white/[0.06] transition-all duration-150 text-xs font-medium"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Sign out</span>
        </button>
      </div>
    </header>
  );
}
