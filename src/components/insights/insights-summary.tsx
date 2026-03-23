'use client';

import { motion } from 'framer-motion';
import { UserInsight } from '@/types/analysis';

interface InsightsSummaryProps {
  latestInsight: UserInsight;
  boundaryBreakdown: { strong: number; developing: number; weak: number };
  totalAnalyses: number;
  allGrowthAreas: Array<{ area: string; count: number }>;
}

const BOUNDARY_COLORS: Record<string, string> = {
  strong: 'text-white/70',
  developing: 'text-white/50',
  weak: 'text-white/30',
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
        className="p-4 bg-white/[0.02] border border-white/[0.08] rounded-xl space-y-3"
      >
        <div className="flex items-center justify-between">
          <p className="text-[10px] text-white/30 font-mono uppercase tracking-wider">
            Latest Snapshot
          </p>
          <span className="text-[10px] font-mono text-white/30 bg-white/5 px-2 py-0.5 rounded-full">
            {latestInsight.overall_tone}
          </span>
        </div>

        <div>
          <p className="text-[10px] text-white/30 font-mono uppercase tracking-wider mb-1">
            Communication Style
          </p>
          <p className="text-sm text-white/60 leading-relaxed">
            {latestInsight.communication_style}
          </p>
        </div>

        <div>
          <p className="text-[10px] text-white/30 font-mono uppercase tracking-wider mb-1">
            Emotional Patterns
          </p>
          <p className="text-sm text-white/60 leading-relaxed">
            {latestInsight.emotional_patterns}
          </p>
        </div>
      </motion.div>

      {/* Stats row */}
      <div className="grid grid-cols-2 gap-3">
        {/* Boundary awareness breakdown */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="p-4 bg-white/[0.02] border border-white/[0.08] rounded-xl"
        >
          <p className="text-[10px] text-white/30 font-mono uppercase tracking-wider mb-3">
            Boundary Awareness
          </p>
          <p className={`text-lg font-mono font-bold ${BOUNDARY_COLORS[dominantBoundary[0]]} mb-2`}>
            {dominantBoundary[0].charAt(0).toUpperCase() + dominantBoundary[0].slice(1)}
          </p>
          <div className="space-y-1">
            {(['strong', 'developing', 'weak'] as const).map((level) => {
              const count = boundaryBreakdown[level];
              const pct = totalAnalyses > 0 ? Math.round((count / totalAnalyses) * 100) : 0;
              return (
                <div key={level} className="flex items-center gap-2">
                  <div className="flex-1 h-1 bg-white/5 rounded-full overflow-hidden">
                    <div
                      role="progressbar"
                      aria-valuenow={pct}
                      aria-valuemin={0}
                      aria-valuemax={100}
                      aria-label={`${level} boundary awareness: ${pct}%`}
                      className="h-full bg-white/20 rounded-full"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <span className="text-[10px] text-white/30 font-mono w-8 text-right">
                    {pct}%
                  </span>
                </div>
              );
            })}
          </div>
          <div className="flex justify-between mt-1" aria-hidden="true">
            <span className="text-[10px] text-white/20 font-mono">strong</span>
            <span className="text-[10px] text-white/20 font-mono">developing</span>
            <span className="text-[10px] text-white/20 font-mono">weak</span>
          </div>
        </motion.div>

        {/* Recurring growth areas */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="p-4 bg-white/[0.02] border border-white/[0.08] rounded-xl"
        >
          <p className="text-[10px] text-white/30 font-mono uppercase tracking-wider mb-3">
            Recurring Growth Areas
          </p>
          {allGrowthAreas.length === 0 ? (
            <p className="text-xs text-white/25">No patterns yet</p>
          ) : (
            <div className="space-y-2">
              {allGrowthAreas.slice(0, 4).map((g, i) => (
                <div key={i} className="flex items-start gap-2">
                  <span className="text-white/30 font-mono text-xs flex-shrink-0">&rarr;</span>
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
    </div>
  );
}
