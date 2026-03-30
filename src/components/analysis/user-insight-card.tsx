'use client';

import { motion } from 'framer-motion';
import { UserInsight, UserPattern } from '@/types/analysis';
import { PatternIcon } from '@/lib/icon-map';

interface UserInsightCardProps {
  insight: UserInsight;
}

const BOUNDARY_LABELS: Record<UserInsight['boundary_awareness'], { label: string; variant: string }> = {
  strong: { label: 'STRONG', variant: 'bg-neon-cyan/5 text-text-secondary' },
  developing: { label: 'DEVELOPING', variant: 'bg-neon-cyan/10 text-text-secondary' },
  weak: { label: 'WEAK', variant: 'badge-status' },
};

const SENTIMENT_STYLES: Record<UserPattern['sentiment'], string> = {
  positive: 'bg-surface-1 border-surface-3',
  neutral: 'bg-surface-1 border-surface-3',
  needs_attention: 'card-dashed !bg-surface-1',
};

export function UserInsightCard({ insight }: UserInsightCardProps) {
  const boundary = BOUNDARY_LABELS[insight.boundary_awareness];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 2.0 }}
      className="space-y-4"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm text-text-secondary">&#9672;</span>
          <h3 className="label-section">
            Your Mirror
          </h3>
        </div>
        <span className="font-mono text-[10px] text-text-secondary bg-neon-cyan/5 px-2.5 py-1 rounded-sm uppercase tracking-wider">
          {insight.overall_tone}
        </span>
      </div>

      {/* Communication Style + Emotional Patterns */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 2.2 }}
        className="card-dashed space-y-4"
      >
        <div>
          <p className="label-section mb-1">
            Communication Style
          </p>
          <p className="text-sm text-text-secondary leading-relaxed">
            {insight.communication_style}
          </p>
        </div>
        <div>
          <p className="label-section mb-1">
            Emotional Patterns
          </p>
          <p className="text-sm text-text-secondary leading-relaxed">
            {insight.emotional_patterns}
          </p>
        </div>

        {/* Boundary Awareness */}
        <div className="flex items-center justify-between">
          <p className="label-section">
            Boundary Awareness
          </p>
          <span className={`font-mono text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-sm ${boundary.variant}`}>
            {boundary.label}
          </span>
        </div>
      </motion.div>

      {/* Detected Patterns */}
      {insight.detected_patterns.length > 0 && (
        <div className="space-y-2">
          <p className="label-section">
            Observed Patterns
          </p>
          {insight.detected_patterns.map((pattern, index) => (
            <motion.div
              key={`${pattern.area}-${index}`}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 2.4 + index * 0.1 }}
              className={`p-3 border rounded-lg ${SENTIMENT_STYLES[pattern.sentiment]}`}
            >
              <div className="flex items-start gap-2">
                <PatternIcon icon={pattern.icon} area={pattern.area} size={16} className="flex-shrink-0 mt-0.5 text-text-secondary" />
                <div>
                  <p className="font-mono text-[10px] text-text-secondary uppercase tracking-wider mb-0.5">
                    {pattern.area}
                  </p>
                  <p className="text-sm text-text-secondary leading-relaxed">
                    {pattern.observation}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Growth Areas */}
      {insight.growth_areas.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2.8 }}
          className="space-y-2"
        >
          <p className="label-section">
            Growth Areas
          </p>
          {insight.growth_areas.map((area, index) => (
            <div
              key={`growth-${index}`}
              className="flex items-start gap-2 text-sm text-text-secondary"
            >
              <span className="text-text-secondary font-mono flex-shrink-0">&gt;&gt;</span>
              <span>{area}</span>
            </div>
          ))}
        </motion.div>
      )}
    </motion.div>
  );
}
