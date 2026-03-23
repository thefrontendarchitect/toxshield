'use client';

import { motion } from 'framer-motion';

interface PatternAnalysisProps {
  text: string;
}

export function PatternAnalysis({ text }: PatternAnalysisProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-xs text-white/40 font-mono uppercase tracking-[0.15em]">
        Behavioral Pattern Analysis
      </h3>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2, duration: 0.8 }}
        className="p-4 bg-surface border border-white/[0.06] rounded-xl relative scanlines"
      >
        <div className="font-mono text-sm text-white/90 leading-relaxed">
          <span className="text-white/50">▸</span>{' '}
          {text}
        </div>
      </motion.div>
    </div>
  );
}
