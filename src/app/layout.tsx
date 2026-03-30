import type { Metadata, Viewport } from "next";
import { Inter, JetBrains_Mono, Anton } from "next/font/google";
import { Analytics } from "@vercel/analytics/react";
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

const anton = Anton({
  variable: "--font-anton",
  weight: "400",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL("https://toxshield.in"),
  title: "ToxShield — Forensic Relationship Analyzer",
  description:
    "AI-powered behavioral analysis. Log a person, get a threat profile. Know who's toxic before they know you know.",
  openGraph: {
    title: "ToxShield — Forensic Relationship Analyzer",
    description:
      "AI-powered behavioral analysis. Log a person, get a threat profile.",
    url: "https://toxshield.in",
    siteName: "ToxShield",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "ToxShield — Forensic Relationship Analyzer",
    description:
      "AI-powered behavioral analysis. Log a person, get a threat profile.",
  },
  alternates: {
    canonical: "https://toxshield.in",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
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
      className={`${inter.variable} ${jetbrainsMono.variable} ${anton.variable} min-h-full antialiased dark`}
    >
      <body className="min-h-full bg-surface-0 text-text-primary">
        <AppProviders>{children}</AppProviders>
        <Analytics />
      </body>
    </html>
  );
}
