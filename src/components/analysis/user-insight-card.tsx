'use client';

import { motion } from 'framer-motion';
import { UserInsight, UserPattern } from '@/types/analysis';

interface UserInsightCardProps {
  insight: UserInsight;
}

const BOUNDARY_INDICATORS: Record<UserInsight['boundary_awareness'], { filled: number; label: string }> = {
  strong: { filled: 3, label: 'Strong' },
  developing: { filled: 2, label: 'Developing' },
  weak: { filled: 1, label: 'Weak' },
};

const SENTIMENT_STYLES: Record<UserPattern['sentiment'], string> = {
  positive: 'bg-white/5 border-white/10',
  neutral: 'bg-white/5 border-white/15',
  needs_attention: 'bg-white/10 border-white/25',
};

export function UserInsightCard({ insight }: UserInsightCardProps) {
  const boundary = BOUNDARY_INDICATORS[insight.boundary_awareness];

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
          <span className="text-base text-white/50">&#x25C8;</span>
          <h3 className="font-mono text-xs font-bold text-white/70 uppercase tracking-[0.15em]">
            Your Mirror
          </h3>
        </div>
        <span className="text-[14px] font-mono text-white/30 bg-white/5 px-2 py-0.5 rounded-full">
          {insight.overall_tone}
        </span>
      </div>

      {/* Communication Style + Emotional Patterns */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 2.2 }}
        className="p-4 bg-white/[0.02] border border-white/[0.08] rounded-lg space-y-3"
      >
        <div>
          <p className="text-[14px] text-white/30 font-mono uppercase tracking-wider mb-1">
            Communication Style
          </p>
          <p className="text-sm text-white/60 leading-relaxed">
            {insight.communication_style}
          </p>
        </div>
        <div>
          <p className="text-[14px] text-white/30 font-mono uppercase tracking-wider mb-1">
            Emotional Patterns
          </p>
          <p className="text-sm text-white/60 leading-relaxed">
            {insight.emotional_patterns}
          </p>
        </div>

        {/* Boundary Awareness */}
        <div className="flex items-center justify-between">
          <p className="text-[14px] text-white/30 font-mono uppercase tracking-wider">
            Boundary Awareness
          </p>
          <div className="flex items-center gap-1.5">
            {[1, 2, 3].map((i) => (
              <span
                key={i}
                className={`text-xs ${i <= boundary.filled ? 'text-white/60' : 'text-white/15'}`}
              >
                {i <= boundary.filled ? '\u25CF' : '\u25CB'}
              </span>
            ))}
            <span className="text-[14px] text-white/40 font-mono ml-1">
              {boundary.label}
            </span>
          </div>
        </div>
      </motion.div>

      {/* Detected Patterns */}
      {insight.detected_patterns.length > 0 && (
        <div className="space-y-2">
          <p className="text-[14px] text-white/30 font-mono uppercase tracking-wider">
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
                <span className="text-sm flex-shrink-0">{pattern.icon}</span>
                <div>
                  <p className="text-xs font-mono text-white/50 mb-0.5">
                    {pattern.area}
                  </p>
                  <p className="text-sm text-white/60 leading-relaxed">
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
          <p className="text-[14px] text-white/30 font-mono uppercase tracking-wider">
            Growth Areas
          </p>
          {insight.growth_areas.map((area, index) => (
            <div
              key={`growth-${index}`}
              className="flex items-start gap-2 text-sm text-white/50"
            >
              <span className="text-white/40 font-mono flex-shrink-0">&rarr;</span>
              <span>{area}</span>
            </div>
          ))}
        </motion.div>
      )}
    </motion.div>
  );
}
