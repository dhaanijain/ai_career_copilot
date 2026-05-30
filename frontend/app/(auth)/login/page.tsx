"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { Eye, EyeOff, Sparkles, Loader2, Mail, Lock } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/context/ToastContext";

export default function LoginPage() {
  const router = useRouter();
  const { signIn } = useAuth();
  const { toast } = useToast();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});

  const validate = () => {
    const errs: { email?: string; password?: string } = {};
    if (!email) errs.email = "Email is required";
    else if (!/\S+@\S+\.\S+/.test(email)) errs.email = "Enter a valid email address";
    if (!password) errs.password = "Password is required";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    try {
      await signIn(email, password);
      toast("success", "Welcome back!");
      router.push("/dashboard");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Sign in failed";
      if (msg.includes("Invalid login credentials")) {
        toast("error", "Invalid email or password. Please try again.");
      } else if (msg.includes("Email not confirmed")) {
        toast("info", "Please check your email and confirm your account first.");
      } else if (msg.includes("network") || msg.includes("fetch")) {
        toast("error", "Network error. Check your connection and try again.");
      } else {
        toast("error", msg || "Sign in failed. Please try again.");
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
        <div className="grid lg:grid-cols-2 min-h-[580px]">
          {/* Left — Branding */}
          <div className="relative hidden lg:flex flex-col justify-between p-10 border-r border-white/[0.06] overflow-hidden">
            {/* Background gradient */}
            <div className="absolute inset-0 bg-gradient-to-br from-purple-600/[0.12] to-transparent pointer-events-none" />
            <div className="absolute bottom-0 left-0 w-72 h-72 rounded-full bg-purple-600/10 blur-3xl pointer-events-none" />

            {/* Logo */}
            <div className="relative flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-purple-600 to-purple-400 flex items-center justify-center shadow-[0_0_20px_rgba(139,92,246,0.5)]">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="font-display font-semibold text-white tracking-tight">Career Copilot</span>
            </div>

            {/* Headline + bullets */}
            <div className="relative">
              <h1 className="font-display font-bold text-[2.5rem] leading-tight text-white mb-4">
                Welcome Back
              </h1>
              <p className="text-[#A1A1AA] leading-relaxed mb-8">
                Sign in to access your career insights.
              </p>
              <div className="space-y-3">
                {[
                  "Resume analysis & skill extraction",
                  "Semantic job matching",
                  "Skill gap intelligence",
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

            <div className="mb-8">
              <h2 className="font-display font-bold text-2xl text-white mb-1.5">Sign in</h2>
              <p className="text-sm text-[#A1A1AA]">Enter your credentials to continue</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4" noValidate>
              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-[#A1A1AA] mb-1.5">
                  Email
                </label>
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
                <div className="flex items-center justify-between mb-1.5">
                  <label className="block text-sm font-medium text-[#A1A1AA]">
                    Password
                  </label>
                  <span className="text-xs text-purple-400 hover:text-purple-300 transition-colors cursor-pointer">
                    Forgot password?
                  </span>
                </div>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#A1A1AA] pointer-events-none" />
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => {
                      setPassword(e.target.value);
                      if (errors.password)
                        setErrors((p) => ({ ...p, password: undefined }));
                    }}
                    placeholder="••••••••"
                    autoComplete="current-password"
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
                    {showPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
                {errors.password && (
                  <p className="text-xs text-red-400 mt-1.5">{errors.password}</p>
                )}
              </div>

              {/* Submit */}
              <motion.button
                type="submit"
                disabled={loading}
                whileHover={{ scale: loading ? 1 : 1.01 }}
                whileTap={{ scale: loading ? 1 : 0.99 }}
                className="w-full mt-2 flex items-center justify-center gap-2 px-6 py-3 rounded-xl text-white text-sm font-semibold disabled:opacity-60 disabled:cursor-not-allowed transition-all duration-200"
                style={{
                  background: "linear-gradient(135deg, #9333ea, #7c3aed)",
                  boxShadow: loading
                    ? "none"
                    : "0 0 20px rgba(139,92,246,0.35)",
                }}
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Signing in…
                  </>
                ) : (
                  "Sign In"
                )}
              </motion.button>
            </form>

            <p className="text-sm text-center text-[#A1A1AA] mt-6">
              Don&apos;t have an account?{" "}
              <Link
                href="/signup"
                className="text-purple-400 hover:text-purple-300 font-medium transition-colors"
              >
                Sign Up
              </Link>
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
