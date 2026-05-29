import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Career Copilot",
  description: "AI-powered career platform for resume analysis, job matching, and skill gap intelligence",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#07070A] text-[#FAFAFA] antialiased">
        {children}
      </body>
    </html>
  );
}
