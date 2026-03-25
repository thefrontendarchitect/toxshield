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
      className="card-dashed"
    >
      <div className="flex items-start gap-3 mb-4">
        <span className="text-lg text-white/40">&#9671;</span>
        <div>
          <h3 className="label-section mb-2">
            SELF-REFLECTION MODE
          </h3>
          <p className="text-sm text-white/60 leading-relaxed">
            {reflection.message}
          </p>
        </div>
      </div>

      <div className="space-y-2 pl-8">
        <p className="label-section mb-2">
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
            <span className="text-white/40 font-mono flex-shrink-0">&gt;&gt;</span>
            <span>{suggestion}</span>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
