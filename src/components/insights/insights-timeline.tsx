'use client';

import { motion } from 'framer-motion';
import { UserPattern } from '@/types/analysis';
import Link from 'next/link';

interface TimelineEntry {
  personName: string;
  personId: string;
  date: string;
  overallTone: string;
  communicationStyle: string;
  boundaryAwareness: 'strong' | 'developing' | 'weak';
}

interface InsightsTimelineProps {
  timeline: TimelineEntry[];
  allPatterns: Array<UserPattern & { personName: string; date: string }>;
}

const BOUNDARY_LABELS: Record<string, { label: string; style: string }> = {
  strong: { label: 'FIXED', style: 'bg-neon-cyan/5 text-text-secondary' },
  developing: { label: 'MONITORED', style: 'bg-neon-cyan/10 text-text-secondary' },
  weak: { label: 'BREACHED', style: 'badge-status' },
};

const SENTIMENT_STYLES: Record<UserPattern['sentiment'], string> = {
  positive: 'bg-surface-1 border-surface-3',
  neutral: 'bg-surface-1 border-surface-3',
  needs_attention: 'card-dashed !bg-surface-1',
};

function formatDate(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

export function InsightsTimeline({ timeline, allPatterns }: InsightsTimelineProps) {
  return (
    <div className="space-y-4">
      {/* Patterns across all analyses */}
      {allPatterns.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <p className="label-section mb-3">
            Observed Patterns Across Analyses
          </p>
          <div className="space-y-2">
            {allPatterns.slice(0, 10).map((pattern, i) => (
              <motion.div
                key={`${pattern.personName}-${pattern.area}-${i}`}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + i * 0.05 }}
                className={`p-3 border rounded-lg ${SENTIMENT_STYLES[pattern.sentiment]}`}
              >
                <div className="flex items-start gap-2">
                  <span className="text-sm flex-shrink-0">{pattern.icon}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="font-mono text-[10px] text-text-secondary uppercase tracking-wider">
                        {pattern.area}
                      </span>
                      <span className="font-mono text-[10px] text-text-secondary">
                        re: {pattern.personName}
                      </span>
                    </div>
                    <p className="text-sm text-text-secondary leading-relaxed">
                      {pattern.observation}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Timeline */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <p className="label-section mb-3">
          Analysis Timeline
        </p>
        <div className="space-y-2">
          {timeline.map((entry) => {
            const boundary = BOUNDARY_LABELS[entry.boundaryAwareness];
            return (
              <Link
                key={`${entry.personId}-${entry.date}`}
                href={`/people/${entry.personId}`}
                className="flex items-center justify-between p-3 bg-surface-1 border border-surface-3 rounded-lg hover:bg-surface-2 active:bg-surface-2 transition-colors"
              >
                <div className="flex items-center gap-3 min-w-0 flex-1">
                  <span className="font-mono text-[10px] text-text-secondary flex-shrink-0 w-10">
                    {formatDate(entry.date)}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="font-mono text-xs text-text-secondary truncate uppercase">
                      {entry.personName}
                    </p>
                    <p className="font-mono text-[10px] text-text-secondary truncate">
                      {entry.overallTone}
                    </p>
                  </div>
                </div>
                <span className={`font-mono text-[8px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded-sm flex-shrink-0 ml-2 ${boundary.style}`}>
                  {boundary.label}
                </span>
              </Link>
            );
          })}
        </div>
      </motion.div>
    </div>
  );
}
