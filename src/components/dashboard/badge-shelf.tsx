'use client';

import { motion } from 'framer-motion';

interface Badge {
  id: string;
  name: string;
  description: string;
  icon: string;
  earned: boolean;
}

interface BadgeShelfProps {
  badges: Badge[];
}

export function BadgeShelf({ badges }: BadgeShelfProps) {
  const earned = badges.filter((b) => b.earned);
  const locked = badges.filter((b) => !b.earned);

  if (badges.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="space-y-2"
    >
      <p className="label-section">BADGES</p>
      <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide -mx-1 px-1">
        {earned.map((badge) => (
          <div
            key={badge.id}
            className="shrink-0 flex flex-col items-center gap-1 w-14"
            title={`${badge.name}: ${badge.description}`}
          >
            <span className="text-2xl">{badge.icon}</span>
            <span className="font-mono text-[8px] text-text-secondary text-center truncate w-full">
              {badge.name}
            </span>
          </div>
        ))}
        {locked.map((badge) => (
          <div
            key={badge.id}
            className="shrink-0 flex flex-col items-center gap-1 w-14 opacity-20"
            title={`Locked: ${badge.description}`}
          >
            <span className="text-2xl grayscale">{badge.icon}</span>
            <span className="font-mono text-[8px] text-text-secondary text-center truncate w-full">
              ???
            </span>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
