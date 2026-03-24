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

const BOUNDARY_DOTS: Record<string, number> = {
  strong: 3,
  developing: 2,
  weak: 1,
};

const SENTIMENT_STYLES: Record<UserPattern['sentiment'], string> = {
  positive: 'bg-white/5 border-white/10',
  neutral: 'bg-white/5 border-white/15',
  needs_attention: 'bg-white/10 border-white/25',
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
          <p className="text-[14px] text-white/30 font-mono uppercase tracking-wider mb-3">
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
                      <span className="text-xs font-mono text-white/50">
                        {pattern.area}
                      </span>
                      <span className="text-[14px] text-white/20 font-mono">
                        re: {pattern.personName}
                      </span>
                    </div>
                    <p className="text-sm text-white/60 leading-relaxed">
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
        <p className="text-[14px] text-white/30 font-mono uppercase tracking-wider mb-3">
          Analysis Timeline
        </p>
        <div className="space-y-2">
          {timeline.map((entry) => {
            const filled = BOUNDARY_DOTS[entry.boundaryAwareness];
            return (
              <Link
                key={`${entry.personId}-${entry.date}`}
                href={`/people/${entry.personId}`}
                className="flex items-center justify-between p-3 bg-white/[0.02] border border-white/[0.08] rounded-lg hover:bg-white/[0.04] active:bg-white/[0.06] transition-colors"
              >
                <div className="flex items-center gap-3 min-w-0 flex-1">
                  <span className="text-[14px] text-white/20 font-mono flex-shrink-0 w-10">
                    {formatDate(entry.date)}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-mono text-white/60 truncate">
                      {entry.personName}
                    </p>
                    <p className="text-[14px] text-white/30 truncate">
                      {entry.overallTone}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-1 flex-shrink-0 ml-2">
                  {[1, 2, 3].map((dot) => (
                    <span
                      key={dot}
                      className={`text-[10px] ${dot <= filled ? 'text-white/50' : 'text-white/15'}`}
                    >
                      {dot <= filled ? '\u25CF' : '\u25CB'}
                    </span>
                  ))}
                </div>
              </Link>
            );
          })}
        </div>
      </motion.div>
    </div>
  );
}
