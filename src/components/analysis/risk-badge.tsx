'use client';

import { motion } from 'framer-motion';
import { RiskLevel } from '@/types/analysis';
import { RISK_LABELS } from '@/lib/constants';

interface RiskBadgeProps {
  level: RiskLevel;
}

export function RiskBadge({ level }: RiskBadgeProps) {
  const isHigh = level === 'high';
  const isModerate = level === 'moderate';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
      className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border font-mono text-sm tracking-wider ${
        isHigh
          ? 'border-white bg-white text-black font-bold'
          : isModerate
          ? 'border-white/40 bg-white/5 text-white/70 font-medium'
          : 'border-white/20 bg-transparent text-white/40 font-light'
      }`}
    >
      <span
        className={`w-2 h-2 rounded-full ${
          isHigh
            ? 'bg-black animate-pulse'
            : isModerate
            ? 'bg-white/50'
            : 'bg-white/25'
        }`}
      />
      {RISK_LABELS[level]}
    </motion.div>
  );
}
