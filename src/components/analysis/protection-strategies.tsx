'use client';

import { motion } from 'framer-motion';
import { ProtectionStrategy } from '@/types/analysis';

interface ProtectionStrategiesProps {
  strategies: ProtectionStrategy[];
}

const priorityStyles = {
  essential: {
    card: 'card-dashed',
    badge: 'badge-status',
  },
  recommended: {
    card: 'bg-surface-1 border border-surface-3 rounded-lg p-5',
    badge: 'bg-neon-cyan/10 text-text-secondary font-mono text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-sm',
  },
  optional: {
    card: 'bg-surface-1/50 border border-surface-3/50 rounded-lg p-5',
    badge: 'bg-neon-cyan/5 text-text-secondary font-mono text-[10px] font-medium uppercase tracking-wider px-2 py-0.5 rounded-sm',
  },
};

export function ProtectionStrategies({ strategies }: ProtectionStrategiesProps) {
  return (
    <div className="space-y-3">
      <h3 className="label-section">
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
              className={styles.card}
            >
              <div className="flex items-start justify-between gap-2 mb-2">
                <h4 className="font-mono text-sm font-bold text-text-primary uppercase">
                  {strategy.title}
                </h4>
                <span className={`flex-shrink-0 ${styles.badge}`}>
                  {strategy.priority}
                </span>
              </div>
              <p className="text-xs text-text-secondary leading-relaxed">
                {strategy.description}
              </p>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
