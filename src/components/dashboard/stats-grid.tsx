'use client';

import { motion } from 'framer-motion';

interface StatsGridProps {
  totalPeople: number;
  highRiskCount: number;
  totalAnalyses: number;
}

export function StatsGrid({ totalPeople, highRiskCount, totalAnalyses }: StatsGridProps) {
  const stats = [
    {
      label: 'People',
      value: totalPeople,
      opacity: 'opacity-100',
      icon: '◎',
    },
    {
      label: 'High Risk',
      value: highRiskCount,
      opacity: highRiskCount > 0 ? 'opacity-100 font-bold' : 'opacity-40',
      icon: '●',
      glow: highRiskCount > 0,
    },
    {
      label: 'Analyses',
      value: totalAnalyses,
      opacity: 'opacity-70',
      icon: '▸',
    },
  ];

  return (
    <div className="grid grid-cols-3 gap-2">
      {stats.map((stat, index) => (
        <motion.div
          key={stat.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className="bg-surface border border-white/[0.06] rounded-xl p-3 text-center"
        >
          <div className="flex items-center justify-center gap-1 mb-1">
            <span className={`font-mono text-xs text-white/40`}>{stat.icon}</span>
            <span className="text-[14px] text-white/30 font-mono uppercase">
              {stat.label}
            </span>
          </div>
          <p className={`text-2xl font-bold font-mono text-white ${stat.opacity} ${stat.glow ? 'text-glow-subtle' : ''}`}>
            {stat.value}
          </p>
        </motion.div>
      ))}
    </div>
  );
}
