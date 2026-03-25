'use client';

import { motion } from 'framer-motion';

interface PatternAnalysisProps {
  text: string;
}

export function PatternAnalysis({ text }: PatternAnalysisProps) {
  return (
    <div className="space-y-3">
      <h3 className="label-section">
        Behavioral Pattern Analysis
      </h3>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2, duration: 0.8 }}
        className="card-dashed relative scanlines"
      >
        <div className="font-mono text-sm text-white/90 leading-relaxed">
          <span className="text-white/40">&gt;&gt;</span>{' '}
          {text}
        </div>
      </motion.div>
    </div>
  );
}
