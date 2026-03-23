'use client';

export function TerminalHeader({ title }: { title?: string }) {
  return (
    <div className="flex items-center gap-2 px-4 py-2 bg-surface border-b border-white/[0.06] font-mono text-xs">
      <div className="flex items-center gap-1.5 text-white/20">
        <span>□</span>
        <span>□</span>
        <span>□</span>
      </div>
      <div className="flex-1 text-center text-white/40">
        <span className="text-white">toxshield</span>
        <span className="text-white/30">@{title ?? 'system'}</span>
        <span className="cursor-blink text-white ml-0.5">_</span>
      </div>
      <div className="w-[52px]" />
    </div>
  );
}
