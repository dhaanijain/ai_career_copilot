"use client";

import { useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileText, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface UploadCardProps {
  onUpload: (file: File) => Promise<void>;
  isProcessing?: boolean;
  statusMessage?: string;
  fileName?: string;
  isSuccess?: boolean;
  error?: string;
}

export default function UploadCard({
  onUpload,
  isProcessing = false,
  statusMessage,
  fileName,
  isSuccess = false,
  error,
}: UploadCardProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [clientError, setClientError] = useState<string | null>(null);

  const MAX_SIZE_BYTES = 5 * 1024 * 1024; // 5 MB

  const handleFile = async (file: File) => {
    setClientError(null);
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setClientError("Only PDF files are accepted.");
      return;
    }
    if (file.size > MAX_SIZE_BYTES) {
      setClientError("File exceeds the 5 MB limit. Please use a smaller PDF.");
      return;
    }
    await onUpload(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  return (
    <div className="relative">
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        className="hidden"
        onChange={handleChange}
      />

      <motion.div
        onClick={() => { if (!isProcessing) { setClientError(null); inputRef.current?.click(); } }}
        onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        whileHover={!isProcessing ? { scale: 1.005 } : {}}
        className={cn(
          "relative border-2 border-dashed rounded-2xl p-10 flex flex-col items-center gap-4 transition-all duration-300 cursor-pointer overflow-hidden",
          isDragOver
            ? "border-purple-500 bg-purple-500/5"
            : isSuccess
            ? "border-emerald-500/40 bg-emerald-500/5 cursor-default"
            : (clientError || error)
            ? "border-red-500/40 bg-red-500/5 cursor-default"
            : isProcessing
            ? "border-purple-500/40 bg-purple-500/5 cursor-default"
            : "border-white/[0.12] bg-[#111114] hover:border-purple-500/40 hover:bg-purple-500/[0.03]"
        )}
      >
        {/* Ambient glow when drag over */}
        {isDragOver && (
          <div className="absolute inset-0 bg-gradient-to-br from-purple-600/10 to-transparent pointer-events-none" />
        )}

        <AnimatePresence mode="wait">
          {isProcessing ? (
            <motion.div
              key="processing"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="flex flex-col items-center gap-3 text-center"
            >
              <div className="relative w-14 h-14 rounded-full bg-purple-500/10 flex items-center justify-center">
                <Loader2 className="w-7 h-7 text-purple-400 animate-spin" />
                <div className="absolute inset-0 rounded-full border-2 border-purple-500/20 animate-ping" />
              </div>
              <div>
                <p className="font-display font-semibold text-white">
                  {statusMessage || "Processing..."}
                </p>
                <p className="text-[#A1A1AA] text-sm mt-1">
                  AI is analyzing your resume
                </p>
              </div>
            </motion.div>
          ) : isSuccess ? (
            <motion.div
              key="success"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="flex flex-col items-center gap-3 text-center"
            >
              <div className="w-14 h-14 rounded-full bg-emerald-500/10 flex items-center justify-center">
                <CheckCircle2 className="w-7 h-7 text-emerald-400" />
              </div>
              <div>
                <p className="font-display font-semibold text-white">
                  Resume Analyzed!
                </p>
                {fileName && (
                  <p className="text-[#A1A1AA] text-sm mt-1">{fileName}</p>
                )}
              </div>
              <p className="text-xs text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full">
                Click to upload a different resume
              </p>
            </motion.div>
          ) : (clientError || error) ? (
            <motion.div
              key="error"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="flex flex-col items-center gap-3 text-center"
            >
              <div className="w-14 h-14 rounded-full bg-red-500/10 flex items-center justify-center">
                <AlertCircle className="w-7 h-7 text-red-400" />
              </div>
              <div>
                <p className="font-display font-semibold text-white">Upload Failed</p>
                <p className="text-red-400 text-sm mt-1">{clientError || error}</p>
              </div>
              <p className="text-xs text-[#A1A1AA]">Click to try again</p>
            </motion.div>
          ) : (
            <motion.div
              key="idle"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="flex flex-col items-center gap-4 text-center"
            >
              <motion.div
                animate={{ y: [0, -4, 0] }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                className="w-14 h-14 rounded-full bg-purple-500/10 border border-purple-500/20 flex items-center justify-center"
              >
                <Upload className="w-6 h-6 text-purple-400" />
              </motion.div>
              <div>
                <p className="font-display font-semibold text-white text-lg">
                  Drop your resume here
                </p>
                <p className="text-[#A1A1AA] text-sm mt-1">
                  or <span className="text-purple-400 font-medium">click to browse</span>
                </p>
              </div>
              <div className="flex items-center gap-2 text-xs text-[#A1A1AA]">
                <FileText className="w-3.5 h-3.5" />
                PDF files only
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
