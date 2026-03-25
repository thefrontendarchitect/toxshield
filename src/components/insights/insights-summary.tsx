'use client';

import { motion } from 'framer-motion';
import { UserInsight } from '@/types/analysis';
import { ShieldIcon } from '@/components/ui/dossier-icons';

interface InsightsSummaryProps {
  latestInsight: UserInsight;
  boundaryBreakdown: { strong: number; developing: number; weak: number };
  totalAnalyses: number;
  allGrowthAreas: Array<{ area: string; count: number }>;
}

const BOUNDARY_BADGE: Record<string, { label: string; style: string }> = {
  strong: { label: 'FIXED', style: 'bg-white/5 text-white/40' },
  developing: { label: 'MONITORED', style: 'bg-white/10 text-white/60' },
  weak: { label: 'BREACHED', style: 'badge-status' },
};

export function InsightsSummary({
  latestInsight,
  boundaryBreakdown,
  totalAnalyses,
  allGrowthAreas,
}: InsightsSummaryProps) {
  const dominantBoundary = (
    Object.entries(boundaryBreakdown) as [string, number][]
  ).sort((a, b) => b[1] - a[1])[0];

  return (
    <div className="space-y-4">
      {/* Latest snapshot */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="card-dashed space-y-4"
      >
        <div className="flex items-center justify-between">
          <p className="label-section">
            Latest Snapshot
          </p>
          <span className="font-mono text-[10px] text-white/30 bg-white/5 px-2.5 py-1 rounded-sm uppercase tracking-wider">
            {latestInsight.overall_tone}
          </span>
        </div>

        <div>
          <p className="label-section mb-1">
            Communication Style
          </p>
          <p className="text-sm text-white/60 leading-relaxed">
            {latestInsight.communication_style}
          </p>
        </div>

        <div>
          <p className="label-section mb-1">
            Emotional Patterns
          </p>
          <p className="text-sm text-white/60 leading-relaxed">
            {latestInsight.emotional_patterns}
          </p>
        </div>
      </motion.div>

      {/* Boundary Awareness Section */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-surface-1 border border-surface-3 rounded-lg p-5"
      >
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-mono text-lg font-bold uppercase text-white">BOUNDARY AWARENESS</h3>
          <ShieldIcon size={20} className="text-white/30" />
        </div>
        <p className="label-section mb-4">INTEGRITY OF DIGITAL DEFENSES</p>

        <div className="space-y-3">
          {(['strong', 'developing', 'weak'] as const).map((level) => {
            const count = boundaryBreakdown[level];
            const pct = totalAnalyses > 0 ? Math.round((count / totalAnalyses) * 100) : 0;
            const badge = BOUNDARY_BADGE[level];
            return (
              <div key={level} className="card-dashed flex items-center justify-between !p-3">
                <div className="flex items-center gap-3">
                  <ShieldIcon size={16} className={level === 'weak' ? 'text-badge-pink' : 'text-white/30'} />
                  <div>
                    <p className="font-mono text-xs uppercase text-white/60">{level}</p>
                    <p className="font-mono text-[10px] text-white/30">{pct}% of analyses</p>
                  </div>
                </div>
                <span className={`font-mono text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-sm ${badge.style}`}>
                  {badge.label}
                </span>
              </div>
            );
          })}
        </div>
      </motion.div>

      {/* Recurring growth areas */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card-dashed"
      >
        <p className="label-section mb-3">
          Recurring Growth Areas
        </p>
        {allGrowthAreas.length === 0 ? (
          <p className="font-mono text-[10px] text-white/25 uppercase">No patterns yet</p>
        ) : (
          <div className="space-y-2">
            {allGrowthAreas.slice(0, 4).map((g, i) => (
              <div key={i} className="flex items-start gap-2">
                <span className="text-white/30 font-mono text-xs flex-shrink-0">&gt;&gt;</span>
                <p className="text-xs text-white/50 leading-relaxed line-clamp-2">
                  {g.area}
                  {g.count > 1 && (
                    <span className="text-white/20 ml-1">({g.count}x)</span>
                  )}
                </p>
              </div>
            ))}
          </div>
        )}
      </motion.div>
    </div>
  );
}
