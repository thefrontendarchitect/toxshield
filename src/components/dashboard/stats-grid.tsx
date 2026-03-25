'use client';

import { motion } from 'framer-motion';
import { FingerprintIcon } from '@/components/ui/dossier-icons';

interface StatsGridProps {
  totalPeople: number;
  highRiskCount: number;
  totalAnalyses: number;
}

export function StatsGrid({ totalPeople, highRiskCount, totalAnalyses }: StatsGridProps) {
  const riskRatio = totalPeople > 0 ? highRiskCount / totalPeople : 0;
  const analyzedRatio = totalPeople > 0 ? Math.min(totalAnalyses / totalPeople, 1) : 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-dashed relative overflow-hidden"
    >
      {/* Fingerprint watermark */}
      <div className="absolute top-3 right-3 opacity-[0.03]">
        <FingerprintIcon size={80} className="text-white" />
      </div>

      {/* Section label */}
      <p className="label-section mb-3">TOTAL SUBJECTS</p>

      {/* Large stat number */}
      <div className="flex items-baseline gap-3 mb-2">
        <span className="font-mono text-6xl font-black italic text-white leading-none">
          {totalPeople.toLocaleString()}
        </span>
        {highRiskCount > 0 && (
          <span className="font-mono text-sm font-bold text-badge-pink">
            {highRiskCount} HIGH RISK
          </span>
        )}
      </div>

      {/* Subtext */}
      <p className="text-xs text-white/30 font-mono mb-4">
        {totalAnalyses} analyses conducted across all subjects
      </p>

      {/* Progress bars */}
      <div className="flex gap-1.5">
        <div className="flex-1 h-1 bg-white/5 rounded-full overflow-hidden">
          <div className="h-full bg-white/30 rounded-full" style={{ width: `${Math.min(totalPeople * 10, 100)}%` }} />
        </div>
        <div className="flex-1 h-1 bg-white/5 rounded-full overflow-hidden">
          <div className="h-full bg-white/30 rounded-full" style={{ width: `${analyzedRatio * 100}%` }} />
        </div>
        <div className="flex-1 h-1 bg-white/5 rounded-full overflow-hidden">
          <div className="h-full bg-white/20 rounded-full" style={{ width: `${riskRatio * 100}%` }} />
        </div>
        <div className="flex-1 h-1 bg-white/5 rounded-full overflow-hidden">
          <div className="h-full bg-white/15 rounded-full" style={{ width: '60%' }} />
        </div>
      </div>
    </motion.div>
  );
}
