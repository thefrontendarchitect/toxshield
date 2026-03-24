import type { Metadata, Viewport } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { AppProviders } from "@/components/providers/app-providers";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ToxShield — Forensic Relationship Analyzer",
  description:
    "AI-powered behavioral analysis. Log a person, get a threat profile. Know who's toxic before they know you know.",
  openGraph: {
    title: "ToxShield — Forensic Relationship Analyzer",
    description:
      "AI-powered behavioral analysis. Log a person, get a threat profile.",
    type: "website",
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  minimumScale: 1,
  userScalable: false,
  viewportFit: 'cover',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${jetbrainsMono.variable} min-h-full antialiased dark`}
    >
      <body className="min-h-full bg-surface-0 text-text-primary">
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
