'use client';

import { motion } from 'framer-motion';

interface StreakCounterProps {
  currentStreak: number;
  longestStreak: number;
}

export function StreakCounter({ currentStreak, longestStreak }: StreakCounterProps) {
  const isActive = currentStreak > 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="arcane-glass p-4"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className={`text-2xl ${isActive ? 'animate-pulse' : 'opacity-30'}`}>
            🔥
          </span>
          <div>
            <p className="font-mono text-2xl font-black italic text-text-primary">
              {currentStreak}
            </p>
            <p className="font-mono text-[10px] text-text-secondary uppercase tracking-[0.15em]">
              Week Streak
            </p>
          </div>
        </div>

        <div className="text-right">
          <p className="font-mono text-xs text-text-secondary uppercase tracking-wider">
            Best
          </p>
          <p className="font-mono text-lg font-bold text-neon-cyan/60">
            {longestStreak}
          </p>
        </div>
      </div>
    </motion.div>
  );
}
