"use client";

import { motion } from "framer-motion";
import { FileText, Sparkles, RotateCcw } from "lucide-react";
import { useResume } from "@/context/ResumeContext";
import { useResumeUpload } from "@/hooks/useResumeUpload";
import UploadCard from "@/components/ui/UploadCard";
import SkillChip from "@/components/ui/SkillChip";
import AIInsightCard from "@/components/ui/AIInsightCard";
import GradientButton from "@/components/ui/GradientButton";
import AnalyticsCard from "@/components/ui/AnalyticsCard";

export default function ResumePage() {
  const { resumeSkills, fileName, clearSession } = useResume();
  const {
    upload,
    reset,
    isProcessing,
    isSuccess,
    statusMessage,
    error,
    fileName: uploadFileName,
  } = useResumeUpload();

  const showResults = isSuccess || resumeSkills.length > 0;
  const currentFileName = uploadFileName || fileName;

  const handleReset = () => {
    clearSession();
    reset();
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-2 text-purple-400 text-sm font-medium mb-2">
          <FileText className="w-4 h-4" />
          Resume Analysis
        </div>
        <h1 className="font-display font-bold text-3xl text-white">
          AI Resume Parser
        </h1>
        <p className="text-[#A1A1AA] text-sm mt-1.5">
          Upload your PDF resume. Our pipeline runs OCR → chunking → embeddings → skill extraction.
        </p>
      </motion.div>

      <div className="grid lg:grid-cols-5 gap-6">
        {/* Upload Panel */}
        <div className="lg:col-span-2 space-y-4">
          <UploadCard
            onUpload={upload}
            isProcessing={isProcessing}
            statusMessage={statusMessage}
            fileName={currentFileName ?? undefined}
            isSuccess={isSuccess}
            error={error ?? undefined}
          />

          {showResults && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-center"
            >
              <button
                onClick={handleReset}
                className="flex items-center gap-1.5 text-xs text-[#A1A1AA] hover:text-white transition-colors"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                Reset & upload new resume
              </button>
            </motion.div>
          )}

          {showResults && (
            <div className="grid grid-cols-1 gap-3">
              <AnalyticsCard
                label="Skills Detected"
                value={resumeSkills.length}
                icon={<Sparkles className="w-4 h-4" />}
                color="purple"
                delay={0.1}
              />
            </div>
          )}
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-3 space-y-5">
          {!showResults && !isProcessing && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="h-full flex flex-col items-center justify-center gap-4 text-center bg-[#111114] border border-white/[0.08] rounded-2xl p-10"
            >
              <FileText className="w-10 h-10 text-[#A1A1AA]" />
              <div>
                <p className="font-display font-semibold text-white">Upload your resume</p>
                <p className="text-[#A1A1AA] text-sm mt-1">
                  Extracted skills will appear here
                </p>
              </div>
            </motion.div>
          )}

          {showResults && resumeSkills.length > 0 && (
            <>
              <motion.div
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-[#111114] border border-white/[0.08] rounded-2xl p-6"
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-display font-semibold text-white">Extracted Skills</h3>
                  <span className="text-xs text-[#A1A1AA] bg-white/[0.06] px-2.5 py-1 rounded-full">
                    {resumeSkills.length} detected
                  </span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {resumeSkills.map((skill, i) => (
                    <motion.div
                      key={skill}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: i * 0.03 }}
                    >
                      <SkillChip skill={skill} variant="neutral" />
                    </motion.div>
                  ))}
                </div>
              </motion.div>

              <AIInsightCard
                title="AI Extraction Summary"
                insights={[
                  `${resumeSkills.length} technical skills extracted using whitelist matching + FAISS semantic retrieval.`,
                  "Skills are confidence-scored: whitelist matches in skill sections get highest confidence.",
                  "Use JD Match or Job Recommendations to see how your skills compare to market demand.",
                ]}
                delay={0.2}
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
