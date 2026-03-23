'use client';

import { useRouter } from 'next/navigation';

interface AppHeaderProps {
  title?: string;
  showBackButton?: boolean;
  rightAction?: React.ReactNode;
}

export function AppHeader({
  title = 'TOXSHIELD',
  showBackButton = false,
  rightAction,
}: AppHeaderProps) {
  const router = useRouter();

  return (
    <header className="fixed top-0 left-0 right-0 z-50 flex min-h-[56px] items-center gap-3 px-4 bg-black/95 backdrop-blur-md border-b border-white/[0.06] pt-safe">
      {showBackButton && (
        <button
          type="button"
          onClick={() => router.back()}
          className="flex items-center justify-center min-w-[44px] min-h-[44px] rounded-full active:bg-white/10 transition-colors"
          aria-label="Go back"
        >
          <span className="font-mono text-white text-lg">←</span>
        </button>
      )}

      <h1 className="flex-1 min-w-0 font-mono text-sm font-bold text-white truncate tracking-[0.2em]">
        {title}
      </h1>

      {rightAction && (
        <div className="flex items-center gap-2">{rightAction}</div>
      )}

      {/* Subtle pulsing line at bottom */}
      <div className="absolute bottom-0 left-0 right-0 h-px bg-white/10 line-pulse" />
    </header>
  );
}
