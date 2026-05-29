import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./context/**/*.{js,ts,jsx,tsx,mdx}",
    "./hooks/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#07070A",
        surface: "#111114",
        "surface-2": "#18181C",
        border: "rgba(255,255,255,0.08)",
        purple: {
          DEFAULT: "#8B5CF6",
          soft: "#A78BFA",
          dim: "rgba(139,92,246,0.15)",
        },
        blue: {
          accent: "#38BDF8",
          dim: "rgba(56,189,248,0.10)",
        },
        text: {
          primary: "#FAFAFA",
          secondary: "#A1A1AA",
        },
        success: "#22C55E",
        error: "#EF4444",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["Space Grotesk", "Inter", "system-ui", "sans-serif"],
      },
      borderRadius: {
        "2xl": "1rem",
        "3xl": "1.5rem",
      },
      boxShadow: {
        purple: "0 0 40px rgba(139,92,246,0.25)",
        "purple-sm": "0 0 20px rgba(139,92,246,0.15)",
        blue: "0 0 30px rgba(56,189,248,0.20)",
        card: "0 4px 24px rgba(0,0,0,0.4)",
      },
      animation: {
        shimmer: "shimmer 2s infinite",
        pulse: "pulse 2s cubic-bezier(0.4,0,0.6,1) infinite",
        "spin-slow": "spin 3s linear infinite",
      },
      keyframes: {
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic": "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
    },
  },
  plugins: [],
};

export default config;
