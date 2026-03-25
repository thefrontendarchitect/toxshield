'use client';

import { motion } from 'framer-motion';
import { HeartCrackIcon } from '@/components/ui/dossier-icons';
import { StatusBadge } from '@/components/ui/status-badge';

interface EnvironmentHealthProps {
  health: number;
}

function getHealthStatus(health: number) {
  if (health >= 70) return { label: 'STABLE ENVIRONMENT', variant: 'stable' as const };
  if (health >= 40) return { label: 'ELEVATED RISK DETECTED', variant: 'warning' as const };
  return { label: 'CRITICAL FRACTURE DETECTED', variant: 'critical' as const };
}

export function EnvironmentHealth({ health }: EnvironmentHealthProps) {
  const status = getHealthStatus(health);

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
          <span className="font-mono text-5xl font-black italic text-white leading-none">
            {health}%
          </span>
        </div>
      </div>

      {/* Status badge */}
      <StatusBadge label={status.label} variant={status.variant} />
    </motion.div>
  );
}
