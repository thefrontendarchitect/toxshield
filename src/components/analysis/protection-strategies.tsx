'use client';

import { motion } from 'framer-motion';
import { ProtectionStrategy } from '@/types/analysis';

interface ProtectionStrategiesProps {
  strategies: ProtectionStrategy[];
}

const priorityStyles = {
  essential: {
    border: 'border-white/40',
    bg: 'bg-white/[0.06]',
    badge: 'bg-white text-black font-bold',
  },
  recommended: {
    border: 'border-white/20',
    bg: 'bg-white/[0.03]',
    badge: 'border border-white/40 text-white/70',
  },
  optional: {
    border: 'border-white/10',
    bg: 'bg-white/[0.02]',
    badge: 'text-white/30',
  },
};

export function ProtectionStrategies({ strategies }: ProtectionStrategiesProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-xs text-white/40 font-mono uppercase tracking-[0.15em]">
        Protection Strategies
      </h3>
      <div className="grid gap-3">
        {strategies.map((strategy, index) => {
          const styles = priorityStyles[strategy.priority];
          return (
            <motion.div
              key={strategy.title}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.5 + index * 0.2 }}
              className={`p-4 rounded-xl border ${styles.border} ${styles.bg}`}
            >
              <div className="flex items-start justify-between gap-2 mb-2">
                <h4 className="font-mono text-sm font-bold text-white">
                  {strategy.title}
                </h4>
                <span
                  className={`text-[10px] px-2 py-0.5 rounded-full font-mono uppercase tracking-wider flex-shrink-0 ${styles.badge}`}
                >
                  {strategy.priority}
                </span>
              </div>
              <p className="text-xs text-white/40 leading-relaxed">
                {strategy.description}
              </p>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
