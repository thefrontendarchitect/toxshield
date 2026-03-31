import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: '404 — Page Not Found',
  description: 'The page you are looking for does not exist.',
  robots: { index: false, follow: false },
};

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-surface-0 px-4 text-center">
      <p className="font-mono text-[10px] text-neon-magenta tracking-[0.3em] uppercase mb-6">
        // error_404
      </p>
      <h1 className="text-6xl font-black font-display text-text-primary tracking-[0.15em] text-glow mb-4">
        NOT <span className="text-neon-cyan">FOUND</span>
      </h1>
      <div className="flex items-center gap-3 mb-8">
        <div className="h-[1px] w-12 bg-gradient-to-r from-transparent to-neon-cyan/40" />
        <p className="text-xs text-neon-cyan font-mono tracking-[0.2em] uppercase">
          Target Not Located
        </p>
        <div className="h-[1px] w-12 bg-gradient-to-l from-transparent to-neon-cyan/40" />
      </div>
      <p className="text-text-secondary text-sm max-w-md mb-8 leading-relaxed">
        The page you&apos;re looking for doesn&apos;t exist or has been moved.
        The system could not locate the requested resource.
      </p>
      <Link
        href="/"
        className="px-8 py-3.5 bg-neon-cyan text-surface-0 font-mono text-sm font-bold rounded-lg tracking-[0.1em] uppercase glow min-h-[44px] flex items-center touch-active"
      >
        Return to Base
      </Link>
    </div>
  );
}
