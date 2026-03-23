'use client';

import { motion } from 'framer-motion';
import { ToxicTrait } from '@/types/analysis';
import { SEVERITY_STYLES, SEVERITY_BG, SEVERITY_SYMBOLS, SEVERITY_COLORS } from '@/lib/constants';

interface TraitListProps {
  traits: ToxicTrait[];
}

export function TraitList({ traits }: TraitListProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-xs text-white/40 font-mono uppercase tracking-[0.15em]">
        Detected Traits
      </h3>
      <div className="grid gap-2">
        {traits.map((trait, index) => {
          const isCritical = trait.severity === 'critical';
          return (
            <motion.div
              key={trait.name}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.8 + index * 0.15 }}
              className={`flex items-start gap-3 p-3 rounded-xl border ${SEVERITY_BG[trait.severity]}`}
            >
              <span className={`text-lg flex-shrink-0 mt-0.5 ${SEVERITY_COLORS[trait.severity]}`}>
                {SEVERITY_SYMBOLS[trait.severity]}
              </span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className={`font-mono text-sm text-white ${SEVERITY_STYLES[trait.severity]}`}>
                    {trait.name}
                  </span>
                  <span
                    className={`text-[10px] px-1.5 py-0.5 rounded font-mono uppercase tracking-wider ${
                      isCritical
                        ? 'bg-white text-black font-bold'
                        : 'bg-white/10 text-white/50'
                    }`}
                  >
                    {trait.severity}
                  </span>
                </div>
                <p className="text-xs text-white/40 mt-1 leading-relaxed">
                  {trait.description}
                </p>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
