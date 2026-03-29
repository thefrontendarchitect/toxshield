'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { HeartCrackIcon } from '@/components/ui/dossier-icons';
import { StatusBadge } from '@/components/ui/status-badge';

// Arcane doodle SVGs — same shapes as the aurora background graffiti
function DoodleSkull({ color }: { color: string }) {
  return (
    <svg width="32" height="32" viewBox="-30 -30 60 60" fill="none">
      <circle cx="0" cy="0" r="16" stroke={color} strokeWidth="2.5" />
      {/* Spikes */}
      {[0, 1, 2, 3, 4].map(i => {
        const a = -Math.PI + (Math.PI / 5) * i + Math.PI / 10;
        return <line key={i} x1={Math.cos(a) * 16} y1={Math.sin(a) * 16} x2={Math.cos(a) * 26} y2={Math.sin(a) * 26} stroke={color} strokeWidth="2" />;
      })}
      {/* X eyes */}
      {[-1, 1].map(dx => (
        <g key={dx}>
          <line x1={dx * 5.6 - 2.8} y1={-1.6 - 2.8} x2={dx * 5.6 + 2.8} y2={-1.6 + 2.8} stroke={color} strokeWidth="2" />
          <line x1={dx * 5.6 + 2.8} y1={-1.6 - 2.8} x2={dx * 5.6 - 2.8} y2={-1.6 + 2.8} stroke={color} strokeWidth="2" />
        </g>
      ))}
      {/* Teeth */}
      <line x1="-8" y1="5.6" x2="8" y2="5.6" stroke={color} strokeWidth="2" />
      {[0, 1, 2].map(i => <line key={i} x1={-8 + i * 5.3} y1="2.6" x2={-8 + i * 5.3} y2="8.6" stroke={color} strokeWidth="1.5" />)}
    </svg>
  );
}

function DoodleXMark({ color }: { color: string }) {
  return (
    <svg width="32" height="32" viewBox="-20 -20 40 40" fill="none">
      <line x1="-12" y1="-12" x2="12" y2="12" stroke={color} strokeWidth="3" strokeLinecap="round" />
      <line x1="12" y1="-12" x2="-12" y2="12" stroke={color} strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}

function DoodleHexCrystal({ color }: { color: string }) {
  return (
    <svg width="32" height="32" viewBox="-15 -22 30 44" fill="none">
      <polygon points="0,-18 10,-9 10,9 0,18 -10,9 -10,-9" stroke={color} strokeWidth="2" />
      <line x1="0" y1="-15" x2="0" y2="15" stroke={color} strokeWidth="1.5" opacity="0.5" />
    </svg>
  );
}

function DoodleStar({ color }: { color: string }) {
  const pts = Array.from({ length: 8 }, (_, i) => {
    const a = (Math.PI / 4) * i - Math.PI / 2;
    const r = i % 2 === 0 ? 14 : 5;
    return `${Math.cos(a) * r},${Math.sin(a) * r}`;
  }).join(' ');
  return (
    <svg width="32" height="32" viewBox="-18 -18 36 36" fill="none">
      <polygon points={pts} fill={color} />
    </svg>
  );
}

function DoodleRune({ color }: { color: string }) {
  return (
    <svg width="32" height="32" viewBox="-20 -20 40 40" fill="none">
      <circle cx="0" cy="0" r="14" stroke={color} strokeWidth="2" />
      <circle cx="0" cy="0" r="8" stroke={color} strokeWidth="1.5" opacity="0.5" />
      <circle cx="0" cy="0" r="3" fill={color} />
    </svg>
  );
}

const MOOD_ICONS = [
  { value: 1, label: 'Terrible', color: '#ff2878', Icon: DoodleSkull },
  { value: 2, label: 'Bad', color: '#ff5050', Icon: DoodleXMark },
  { value: 3, label: 'Okay', color: '#ffc832', Icon: DoodleHexCrystal },
  { value: 4, label: 'Good', color: '#00b4ff', Icon: DoodleStar },
  { value: 5, label: 'Great', color: '#50ffa0', Icon: DoodleRune },
];

interface EnvironmentHealthProps {
  health: number;
  todayMood?: number | null;
}

function getHealthStatus(health: number) {
  if (health >= 70) return { label: 'STABLE ENVIRONMENT', variant: 'stable' as const };
  if (health >= 40) return { label: 'ELEVATED RISK DETECTED', variant: 'warning' as const };
  return { label: 'CRITICAL FRACTURE DETECTED', variant: 'critical' as const };
}

export function EnvironmentHealth({ health, todayMood }: EnvironmentHealthProps) {
  const status = getHealthStatus(health);
  const [selectedMood, setSelectedMood] = useState<number | null>(todayMood ?? null);
  const [submitting, setSubmitting] = useState(false);

  const handleMoodSelect = async (mood: number) => {
    setSelectedMood(mood);
    setSubmitting(true);
    try {
      await fetch('/api/health-checkin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mood }),
      });
    } catch {
      // Silent failure — mood is optional
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="card-dashed"
    >
      {/* Section label */}
      <p className="label-section mb-4">ENV. HEALTH SCORE</p>

      {/* Heart + Score */}
      <div className="flex items-center gap-5 mb-4">
        <div className="relative shrink-0">
          <HeartCrackIcon size={56} className={health < 40 ? 'opacity-100' : 'opacity-60'} />
        </div>
        <div>
          <span className="font-mono text-5xl font-black italic text-text-primary leading-none text-glow-subtle">
            {health}%
          </span>
        </div>
      </div>

      {/* Status badge */}
      <StatusBadge label={status.label} variant={status.variant} />

      {/* Daily mood check-in */}
      <div className="mt-4 pt-4 border-t border-surface-3">
        <p className="font-mono text-[10px] text-text-secondary uppercase tracking-[0.15em] mb-2">
          {selectedMood ? 'Today\'s mood' : 'How are you feeling today?'}
        </p>
        <div className="flex justify-between gap-1">
          {MOOD_ICONS.map(({ value, label, color, Icon }) => (
            <button
              key={value}
              type="button"
              onClick={() => handleMoodSelect(value)}
              disabled={submitting}
              title={label}
              aria-label={label}
              className={`flex-1 flex items-center justify-center py-2 rounded-lg transition-all touch-active ${
                selectedMood === value
                  ? 'bg-neon-cyan/10 scale-110'
                  : selectedMood
                    ? 'opacity-25'
                    : 'opacity-70 active:bg-surface-2 hover:opacity-100'
              }`}
            >
              <Icon color={color} />
            </button>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
