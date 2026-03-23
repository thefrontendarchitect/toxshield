'use client';

import { motion } from 'framer-motion';
import { SelfReflection } from '@/types/analysis';

interface SelfReflectionCardProps {
  reflection: SelfReflection;
}

export function SelfReflectionCard({ reflection }: SelfReflectionCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.8 }}
      className="p-6 bg-white/5 border border-white/15 rounded-xl"
    >
      <div className="flex items-start gap-3 mb-4">
        <span className="text-xl text-white/60">◇</span>
        <div>
          <h3 className="font-mono text-sm font-bold text-white mb-1">
            SELF-REFLECTION MODE
          </h3>
          <p className="text-sm text-white/70 leading-relaxed">
            {reflection.message}
          </p>
        </div>
      </div>

      <div className="space-y-2 pl-9">
        <p className="text-xs text-white/30 font-mono uppercase tracking-wider mb-2">
          Suggested Approaches
        </p>
        {reflection.suggestions.map((suggestion, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.2 + index * 0.15 }}
            className="flex items-start gap-2 text-sm text-white/50"
          >
            <span className="text-white/60 font-mono flex-shrink-0">→</span>
            <span>{suggestion}</span>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
