import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function pct(value: number, decimals = 0): string {
  return `${value.toFixed(decimals)}%`;
}

export function scoreColor(score: number): string {
  if (score >= 75) return "#22C55E";
  if (score >= 50) return "#8B5CF6";
  if (score >= 25) return "#38BDF8";
  return "#EF4444";
}

export function truncate(str: string, n: number): string {
  return str.length > n ? str.slice(0, n - 1) + "…" : str;
}
