'use client';

import { motion } from 'framer-motion';

interface EnvironmentHealthProps {
  health: number;
}

function getStrokeIntensity(health: number) {
  // Lower health = MORE visible (more dangerous = more white glow)
  if (health >= 70) return { width: 3, opacity: 0.35, glow: 'drop-shadow(0 0 2px rgba(255,255,255,0.1))' };
  if (health >= 40) return { width: 5, opacity: 0.65, glow: 'drop-shadow(0 0 4px rgba(255,255,255,0.3))' };
  return { width: 7, opacity: 1, glow: 'drop-shadow(0 0 8px rgba(255,255,255,0.5))' };
}

export function EnvironmentHealth({ health }: EnvironmentHealthProps) {
  const size = 100;
  const { width: strokeWidth, opacity, glow } = getStrokeIntensity(health);
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (health / 100) * circumference;
  const offset = circumference - progress;
  const center = size / 2;

  return (
    <div className="bg-surface border border-white/[0.06] rounded-xl p-5 flex items-center gap-4">
      <div className="relative shrink-0 inline-flex items-center justify-center" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="#1a1a1a"
            strokeWidth={strokeWidth}
          />
          <motion.circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="#ffffff"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.5, ease: 'easeOut', delay: 0.3 }}
            style={{ opacity, filter: glow }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            className="text-lg font-bold font-mono text-white"
            style={{ opacity }}
            initial={{ opacity: 0 }}
            animate={{ opacity }}
            transition={{ delay: 0.8 }}
          >
            {health}%
          </motion.span>
        </div>
      </div>

      <div className="flex-1 min-w-0">
        <h3 className="text-xs text-white/30 font-mono uppercase tracking-wider mb-1">
          Environment Health
        </h3>
        <p className="text-xs text-white/40 font-mono leading-relaxed">
          {health >= 70
            ? 'Your circle is relatively healthy'
            : health >= 40
            ? 'Some toxic patterns detected'
            : 'High toxicity — consider boundaries'}
        </p>
      </div>
    </div>
  );
}
