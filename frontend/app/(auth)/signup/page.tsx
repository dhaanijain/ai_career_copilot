"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { Eye, EyeOff, Sparkles, Loader2, Mail, Lock, User } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/context/ToastContext";

export default function SignupPage() {
  const router = useRouter();
  const { signUp } = useAuth();
  const { toast } = useToast();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{
    fullName?: string;
    email?: string;
    password?: string;
    confirmPassword?: string;
  }>({});

  const validate = () => {
    const errs: typeof errors = {};
    if (!fullName.trim()) errs.fullName = "Full name is required";
    if (!email) errs.email = "Email is required";
    else if (!/\S+@\S+\.\S+/.test(email)) errs.email = "Enter a valid email address";
    if (!password) errs.password = "Password is required";
    else if (password.length < 8) errs.password = "Password must be at least 8 characters";
    if (!confirmPassword) errs.confirmPassword = "Please confirm your password";
    else if (password !== confirmPassword) errs.confirmPassword = "Passwords do not match";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    try {
      await signUp(email, password, fullName.trim());
      toast("success", "Account created! Check your email to confirm your account.");
      router.push("/login");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Sign up failed";
      if (msg.includes("already registered") || msg.includes("already exists")) {
        toast("error", "An account with this email already exists. Try signing in.");
      } else if (msg.includes("Password should be")) {
        toast("error", "Password is too weak. Use at least 8 characters.");
      } else if (msg.includes("network") || msg.includes("fetch")) {
        toast("error", "Network error. Check your connection and try again.");
      } else {
        toast("error", msg || "Sign up failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="relative z-10 w-full max-w-4xl"
    >
      <div
        className="rounded-3xl overflow-hidden"
        style={{
          background: "rgba(13,13,20,0.8)",
          backdropFilter: "blur(12px)",
          WebkitBackdropFilter: "blur(12px)",
          border: "1px solid rgba(255,255,255,0.08)",
          boxShadow: "0 0 80px rgba(139,92,246,0.12), 0 4px 48px rgba(0,0,0,0.5)",
        }}
      >
        <div className="grid lg:grid-cols-2 min-h-[620px]">
          {/* Left — Branding */}
          <div className="relative hidden lg:flex flex-col justify-between p-10 border-r border-white/[0.06] overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-purple-600/[0.12] to-transparent pointer-events-none" />
            <div className="absolute bottom-0 left-0 w-72 h-72 rounded-full bg-purple-600/10 blur-3xl pointer-events-none" />

            {/* Logo */}
            <div className="relative flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-purple-600 to-purple-400 flex items-center justify-center shadow-[0_0_20px_rgba(139,92,246,0.5)]">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="font-display font-semibold text-white tracking-tight">Career Copilot</span>
            </div>

            {/* Headline */}
            <div className="relative">
              <h1 className="font-display font-bold text-[2.5rem] leading-tight text-white mb-4">
                Start your career journey
              </h1>
              <p className="text-[#A1A1AA] leading-relaxed mb-8">
                Create an account to unlock AI-powered career intelligence.
              </p>
              <div className="space-y-3">
                {[
                  "Upload & analyze your resume instantly",
                  "Match against real job listings",
                  "Get personalized skill recommendations",
                ].map((item) => (
                  <div key={item} className="flex items-center gap-2.5 text-sm text-[#A1A1AA]">
                    <div className="w-1.5 h-1.5 rounded-full bg-purple-400 shrink-0" />
                    {item}
                  </div>
                ))}
              </div>
            </div>

            <p className="relative text-xs text-[#A1A1AA]/40">© 2025 Career Copilot</p>
          </div>

          {/* Right — Form */}
          <div className="flex flex-col justify-center p-8 lg:p-10">
            {/* Mobile logo */}
            <div className="flex items-center gap-2 mb-8 lg:hidden">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-purple-600 to-purple-400 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <span className="font-display font-semibold text-white">Career Copilot</span>
            </div>

            <div className="mb-7">
              <h2 className="font-display font-bold text-2xl text-white mb-1.5">Create account</h2>
              <p className="text-sm text-[#A1A1AA]">Join thousands of job seekers using AI</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-3.5" noValidate>
              {/* Full Name */}
              <div>
                <label className="block text-sm font-medium text-[#A1A1AA] mb-1.5">
                  Full Name
                </label>
                <div className="relative">
                  <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#A1A1AA] pointer-events-none" />
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => {
                      setFullName(e.target.value);
                      if (errors.fullName) setErrors((p) => ({ ...p, fullName: undefined }));
                    }}
                    placeholder="Jane Doe"
                    autoComplete="name"
                    className="w-full pl-10 pr-4 py-3 rounded-xl text-sm text-white placeholder:text-[#A1A1AA]/40 focus:outline-none transition-all duration-200"
                    style={{
                      background: errors.fullName
                        ? "rgba(239,68,68,0.06)"
                        : "rgba(255,255,255,0.04)",
                      border: `1px solid ${errors.fullName ? "rgba(239,68,68,0.4)" : "rgba(255,255,255,0.08)"}`,
                    }}
                    onFocus={(e) => {
                      if (!errors.fullName)
                        e.currentTarget.style.border = "1px solid rgba(139,92,246,0.5)";
                    }}
                    onBlur={(e) => {
                      if (!errors.fullName)
                        e.currentTarget.style.border = "1px solid rgba(255,255,255,0.08)";
                    }}
                  />
                </div>
                {errors.fullName && (
                  <p className="text-xs text-red-400 mt-1.5">{errors.fullName}</p>
                )}
              </div>

              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-[#A1A1AA] mb-1.5">Email</label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#A1A1AA] pointer-events-none" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => {
                      setEmail(e.target.value);
                      if (errors.email) setErrors((p) => ({ ...p, email: undefined }));
                    }}
                    placeholder="you@example.com"
                    autoComplete="email"
                    className="w-full pl-10 pr-4 py-3 rounded-xl text-sm text-white placeholder:text-[#A1A1AA]/40 focus:outline-none transition-all duration-200"
                    style={{
                      background: errors.email
                        ? "rgba(239,68,68,0.06)"
                        : "rgba(255,255,255,0.04)",
                      border: `1px solid ${errors.email ? "rgba(239,68,68,0.4)" : "rgba(255,255,255,0.08)"}`,
                    }}
                    onFocus={(e) => {
                      if (!errors.email)
                        e.currentTarget.style.border = "1px solid rgba(139,92,246,0.5)";
                    }}
                    onBlur={(e) => {
                      if (!errors.email)
                        e.currentTarget.style.border = "1px solid rgba(255,255,255,0.08)";
                    }}
                  />
                </div>
                {errors.email && (
                  <p className="text-xs text-red-400 mt-1.5">{errors.email}</p>
                )}
              </div>

              {/* Password */}
              <div>
                <label className="block text-sm font-medium text-[#A1A1AA] mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#A1A1AA] pointer-events-none" />
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => {
                      setPassword(e.target.value);
                      if (errors.password) setErrors((p) => ({ ...p, password: undefined }));
                    }}
                    placeholder="Min. 8 characters"
                    autoComplete="new-password"
                    className="w-full pl-10 pr-11 py-3 rounded-xl text-sm text-white placeholder:text-[#A1A1AA]/40 focus:outline-none transition-all duration-200"
                    style={{
                      background: errors.password
                        ? "rgba(239,68,68,0.06)"
                        : "rgba(255,255,255,0.04)",
                      border: `1px solid ${errors.password ? "rgba(239,68,68,0.4)" : "rgba(255,255,255,0.08)"}`,
                    }}
                    onFocus={(e) => {
                      if (!errors.password)
                        e.currentTarget.style.border = "1px solid rgba(139,92,246,0.5)";
                    }}
                    onBlur={(e) => {
                      if (!errors.password)
                        e.currentTarget.style.border = "1px solid rgba(255,255,255,0.08)";
                    }}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-[#A1A1AA] hover:text-white transition-colors"
                    tabIndex={-1}
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                {errors.password && (
                  <p className="text-xs text-red-400 mt-1.5">{errors.password}</p>
                )}
              </div>

              {/* Confirm Password */}
              <div>
                <label className="block text-sm font-medium text-[#A1A1AA] mb-1.5">
                  Confirm Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#A1A1AA] pointer-events-none" />
                  <input
                    type={showConfirm ? "text" : "password"}
                    value={confirmPassword}
                    onChange={(e) => {
                      setConfirmPassword(e.target.value);
                      if (errors.confirmPassword)
                        setErrors((p) => ({ ...p, confirmPassword: undefined }));
                    }}
                    placeholder="Repeat your password"
                    autoComplete="new-password"
                    className="w-full pl-10 pr-11 py-3 rounded-xl text-sm text-white placeholder:text-[#A1A1AA]/40 focus:outline-none transition-all duration-200"
                    style={{
                      background: errors.confirmPassword
                        ? "rgba(239,68,68,0.06)"
                        : "rgba(255,255,255,0.04)",
                      border: `1px solid ${
                        errors.confirmPassword ? "rgba(239,68,68,0.4)" : "rgba(255,255,255,0.08)"
                      }`,
                    }}
                    onFocus={(e) => {
                      if (!errors.confirmPassword)
                        e.currentTarget.style.border = "1px solid rgba(139,92,246,0.5)";
                    }}
                    onBlur={(e) => {
                      if (!errors.confirmPassword)
                        e.currentTarget.style.border = "1px solid rgba(255,255,255,0.08)";
                    }}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirm((v) => !v)}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-[#A1A1AA] hover:text-white transition-colors"
                    tabIndex={-1}
                  >
                    {showConfirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                {errors.confirmPassword && (
                  <p className="text-xs text-red-400 mt-1.5">{errors.confirmPassword}</p>
                )}
              </div>

              {/* Submit */}
              <motion.button
                type="submit"
                disabled={loading}
                whileHover={{ scale: loading ? 1 : 1.01 }}
                whileTap={{ scale: loading ? 1 : 0.99 }}
                className="w-full mt-1 flex items-center justify-center gap-2 px-6 py-3 rounded-xl text-white text-sm font-semibold disabled:opacity-60 disabled:cursor-not-allowed transition-all duration-200"
                style={{
                  background: "linear-gradient(135deg, #9333ea, #7c3aed)",
                  boxShadow: loading ? "none" : "0 0 20px rgba(139,92,246,0.35)",
                }}
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Creating account…
                  </>
                ) : (
                  "Create Account"
                )}
              </motion.button>
            </form>

            <p className="text-sm text-center text-[#A1A1AA] mt-6">
              Already have an account?{" "}
              <Link
                href="/login"
                className="text-purple-400 hover:text-purple-300 font-medium transition-colors"
              >
                Sign In
              </Link>
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
