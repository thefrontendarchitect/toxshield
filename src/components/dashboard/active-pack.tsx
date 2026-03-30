'use client';

import { useEffect, useState } from 'react';
import { PACKS, formatPackExpiry } from '@/lib/packs';
import type { ActivePackData } from '@/types/database';
import Link from 'next/link';

export function ActivePack() {
  const [data, setData] = useState<ActivePackData | null>(null);

  useEffect(() => {
    fetch('/api/purchases/active')
      .then(r => r.json())
      .then(d => { if (d.active) setData(d); })
      .catch(() => {});
  }, []);

  if (!data) return null;

  const pack = PACKS[data.pack_type];
  const usagePercent = Math.round((data.analyses_remaining / data.analyses_granted) * 100);

  return (
    <div className="arcane-glass p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="tag-badge">{pack.name}</span>
          <span className="font-mono text-[10px] text-dim">{formatPackExpiry(data.expires_at)}</span>
        </div>
        <span className="font-mono text-sm font-bold text-neon-cyan">
          {data.analyses_remaining}
          <span className="text-dim font-normal">/{data.analyses_granted}</span>
        </span>
      </div>
      <div className="h-1 rounded-full bg-surface-3 overflow-hidden">
        <div
          className="h-full rounded-full bg-neon-cyan transition-all duration-500"
          style={{ width: `${usagePercent}%` }}
        />
      </div>
    </div>
  );
}

export function UpgradePrompt() {
  return (
    <Link href="/pricing" className="block arcane-glass p-4 active:bg-hover transition-colors">
      <div className="flex items-center justify-between">
        <div>
          <p className="font-mono text-xs font-bold text-text-primary uppercase tracking-wider">Get More Analyses</p>
          <p className="font-mono text-[10px] text-dim mt-0.5">Packs start at $1.29</p>
        </div>
        <span className="font-mono text-sm text-neon-cyan">&rarr;</span>
      </div>
    </Link>
  );
}
