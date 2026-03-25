'use client';

import { motion } from 'framer-motion';
import { RiskLevel } from '@/types/analysis';
import { STATUS_LABELS } from '@/lib/constants';

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
      className={`inline-flex items-center px-3 py-1.5 rounded-sm font-mono text-[10px] font-bold uppercase tracking-[0.15em] ${
        isHigh
          ? 'badge-status'
          : isModerate
          ? 'bg-white/10 text-white/70'
          : 'bg-white/5 text-white/40'
      }`}
    >
      {STATUS_LABELS[level]}
    </motion.div>
  );
}
