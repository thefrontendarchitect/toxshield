'use client';

import { motion } from 'framer-motion';
import { AnimatedRing } from '@/components/ui/animated-ring';

interface ToxicityRingProps {
  score: number;
  size?: number;
}

function getStrokeWidth(score: number): number {
  if (score < 4) return 3;
  if (score < 7) return 5;
  return 8;
}

function getOpacity(score: number): number {
  if (score < 4) return 0.35;
  if (score < 7) return 0.65;
  return 1;
}

function getGlow(score: number): string {
  if (score < 4) return 'drop-shadow(0 0 2px rgba(0,180,255,0.15))';
  if (score < 7) return 'drop-shadow(0 0 6px rgba(255,200,50,0.3))';
  return 'drop-shadow(0 0 8px rgba(255,40,120,0.5)) drop-shadow(0 0 20px rgba(255,40,120,0.2))';
}

export function ToxicityRing({ score, size = 160 }: ToxicityRingProps) {
  const strokeWidth = getStrokeWidth(score);
  const opacity = getOpacity(score);
  const glow = getGlow(score);

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <AnimatedRing
        progress={score / 10}
        size={size}
        strokeWidth={strokeWidth}
        opacity={opacity}
        glowFilter={glow}
        showDecorative
      />

      {/* Score text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <motion.span
          className="font-black font-mono italic text-text-primary"
          style={{
            fontSize: score >= 7 ? '2.5rem' : score >= 4 ? '2rem' : '1.5rem',
            opacity,
          }}
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity, scale: 1 }}
          transition={{ duration: 0.5, delay: 1 }}
        >
          {score.toFixed(1)}
        </motion.span>
        <span className="font-mono text-[10px] text-neon-cyan/30 uppercase tracking-[0.1em] mt-0.5">TOX_SCORE</span>
      </div>
    </div>
  );
}
