'use client';

import { motion } from 'framer-motion';

interface AnimatedRingProps {
  /** 0 to 1 */
  progress: number;
  size: number;
  strokeWidth: number;
  opacity: number;
  glowFilter?: string;
  /** Show decorative concentric circles (used by ToxicityRing) */
  showDecorative?: boolean;
}

export function AnimatedRing({
  progress,
  size,
  strokeWidth,
  opacity,
  glowFilter,
  showDecorative,
}: AnimatedRingProps) {
  const radius = (size - strokeWidth - (showDecorative ? 4 : 0)) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - progress * circumference;
  const center = size / 2;

  return (
    <svg width={size} height={size} className="transform -rotate-90">
      {/* Decorative concentric circles */}
      {showDecorative &&
        [0.85, 0.7, 0.55].map((scale) => (
          <circle
            key={scale}
            cx={center}
            cy={center}
            r={radius * scale}
            fill="none"
            stroke="var(--color-neon-cyan)"
            strokeWidth={0.5}
            opacity={0.05}
          />
        ))}

      {/* Background track */}
      <circle
        cx={center}
        cy={center}
        r={radius}
        fill="none"
        stroke="var(--color-surface-3)"
        strokeWidth={strokeWidth}
      />

      {/* Animated progress ring */}
      <motion.circle
        cx={center}
        cy={center}
        r={radius}
        fill="none"
        stroke="var(--color-neon-cyan)"
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeDasharray={circumference}
        initial={{ strokeDashoffset: circumference }}
        animate={{ strokeDashoffset: offset }}
        transition={{ duration: 1.5, ease: 'easeOut', delay: 0.3 }}
        style={{ opacity, filter: glowFilter }}
      />
    </svg>
  );
}
