"use client";

import { motion } from "framer-motion";
import { Settings, Trash2, Info } from "lucide-react";
import { useResume } from "@/context/ResumeContext";
import GradientButton from "@/components/ui/GradientButton";

export default function SettingsPage() {
  const { resumeId, fileName, resumeSkills, clearSession } = useResume();

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <div className="flex items-center gap-2 text-purple-400 text-sm font-medium mb-2">
          <Settings className="w-4 h-4" />
          Settings
        </div>
        <h1 className="font-display font-bold text-3xl text-white">Settings</h1>
        <p className="text-[#A1A1AA] text-sm mt-1.5">Manage your session and preferences.</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-[#111114] border border-white/[0.08] rounded-2xl p-6 space-y-6"
      >
        {/* Resume Session */}
        <div>
          <h3 className="font-semibold text-white mb-4">Resume Session</h3>
          {resumeId ? (
            <div className="space-y-4">
              <div className="bg-[#18181C] rounded-xl p-4 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-[#A1A1AA]">File</span>
                  <span className="text-white font-medium">{fileName || "Unknown"}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-[#A1A1AA]">Session ID</span>
                  <span className="text-white font-mono text-xs">{resumeId.slice(0, 16)}…</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-[#A1A1AA]">Skills extracted</span>
                  <span className="text-white font-medium">{resumeSkills.length}</span>
                </div>
              </div>
              <GradientButton
                variant="outline"
                onClick={clearSession}
                className="flex items-center gap-2"
              >
                <Trash2 className="w-4 h-4 text-red-400" />
                Clear Session
              </GradientButton>
            </div>
          ) : (
            <div className="flex items-center gap-3 bg-[#18181C] rounded-xl p-4 text-[#A1A1AA] text-sm">
              <Info className="w-4 h-4 shrink-0" />
              No active resume session. Upload a resume to get started.
            </div>
          )}
        </div>

        {/* API */}
        <div className="pt-4 border-t border-white/[0.06]">
          <h3 className="font-semibold text-white mb-4">Backend API</h3>
          <div className="bg-[#18181C] rounded-xl p-4 space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-[#A1A1AA]">API URL</span>
              <span className="text-white font-mono text-xs">
                {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}
              </span>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
