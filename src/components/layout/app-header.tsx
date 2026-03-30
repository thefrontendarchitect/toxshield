'use client';

import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { FolderIcon } from '@/components/ui/dossier-icons';

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
    <header className="fixed top-0 left-0 right-0 z-50 flex min-h-[56px] items-center gap-3 px-4 arcane-glass border-b border-neon-cyan/[0.08] pt-safe">
      {showBackButton && (
        <button
          type="button"
          onClick={() => router.back()}
          className="flex items-center justify-center min-w-[44px] min-h-[44px] rounded-full active:bg-neon-cyan/10 transition-colors"
          aria-label="Go back"
        >
          <span className="font-mono text-neon-cyan/60 text-sm">&larr;</span>
        </button>
      )}

      <div className="flex items-center gap-2 flex-1 min-w-0">
        <FolderIcon size={18} className="text-neon-cyan/40 shrink-0" />
        <h1 className="font-mono text-sm font-bold text-text-primary truncate uppercase tracking-[0.1em] text-glow-subtle">
          {title}
        </h1>
      </div>

      {rightAction ? (
        <div className="flex items-center gap-2">{rightAction}</div>
      ) : (
        <Link
          href="/settings"
          className="w-12 h-12 rounded-full bg-surface-2 border border-neon-cyan/20 flex items-center justify-center shrink-0"
          aria-label="Settings"
        >
          <span className="font-mono text-[10px] font-bold text-neon-cyan/50">AG</span>
        </Link>
      )}
    </header>
  );
}
