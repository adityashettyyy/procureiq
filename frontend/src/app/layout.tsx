import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ProcureIQ — Autonomous Quote Collection",
  description: "Get 3 real supplier quotes in 90 seconds. Powered by TinyFish web agents.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-brand-navy text-white antialiased">{children}</body>
    </html>
  );
}
