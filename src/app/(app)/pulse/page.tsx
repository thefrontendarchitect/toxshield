'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';

interface PulseData {
  pulse: {
    total_analyses: number;
    total_users: number;
    total_people: number;
    avg_toxicity_score: number;
    high_risk_percentage: number;
    top_traits: string[];
    analyses_this_week: number;
    avg_score_this_week: number;
    top_threat_types: string[];
  };
  user: {
    total_analyses: number;
    avg_toxicity_score: number | null;
  };
}

export default function PulsePage() {
  const [data, setData] = useState<PulseData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/pulse')
      .then((r) => r.json())
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <p className="font-mono text-xs text-text-secondary animate-pulse">LOADING COMMUNITY DATA...</p>
      </div>
    );
  }

  const pulse = data?.pulse;
  const user = data?.user;

  return (
    <div className="space-y-6">
      {/* Hero */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="text-center space-y-2">
        <span className="tag-badge">LIVE INTEL</span>
        <h1 className="hero-title text-3xl">COMMUNITY PULSE</h1>
        <p className="font-mono text-[10px] text-neon-cyan/30 uppercase tracking-[0.15em]">
          AGGREGATED // ANONYMOUS // REAL-TIME
        </p>
      </motion.div>

      {/* Global Stats */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="grid grid-cols-3 gap-3">
        <div className="arcane-glass p-3 text-center">
          <p className="font-mono text-2xl font-black italic text-text-primary">{pulse?.total_analyses ?? 0}</p>
          <p className="font-mono text-[9px] text-text-secondary uppercase tracking-wider">Analyses</p>
        </div>
        <div className="arcane-glass p-3 text-center">
          <p className="font-mono text-2xl font-black italic text-text-primary">{pulse?.total_users ?? 0}</p>
          <p className="font-mono text-[9px] text-text-secondary uppercase tracking-wider">Agents</p>
        </div>
        <div className="arcane-glass p-3 text-center">
          <p className="font-mono text-2xl font-black italic text-neon-cyan">{pulse?.avg_toxicity_score ?? 0}</p>
          <p className="font-mono text-[9px] text-text-secondary uppercase tracking-wider">Avg Score</p>
        </div>
      </motion.div>

      {/* This Week */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="card-dashed">
        <p className="label-section mb-3">THIS WEEK</p>
        <div className="flex items-center justify-between">
          <div>
            <p className="font-mono text-3xl font-black italic text-text-primary">{pulse?.analyses_this_week ?? 0}</p>
            <p className="font-mono text-[10px] text-text-secondary">analyses performed</p>
          </div>
          <div className="text-right">
            <p className="font-mono text-xl font-bold text-neon-cyan">{pulse?.avg_score_this_week ?? 0}/10</p>
            <p className="font-mono text-[10px] text-text-secondary">avg toxicity</p>
          </div>
        </div>
        {(pulse?.high_risk_percentage ?? 0) > 0 && (
          <p className="mt-2 font-mono text-[10px] text-neon-magenta">
            {pulse?.high_risk_percentage}% of analyses flagged HIGH RISK
          </p>
        )}
      </motion.div>

      {/* Trending Traits */}
      {(pulse?.top_traits ?? []).length > 0 && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="space-y-2">
          <p className="label-section">TRENDING TRAITS</p>
          <div className="flex flex-wrap gap-2">
            {(pulse?.top_traits ?? []).slice(0, 8).map((trait: string, i: number) => (
              <span
                key={trait}
                className={`px-3 py-1.5 rounded-full font-mono text-[11px] border ${
                  i === 0
                    ? 'bg-neon-magenta/10 border-neon-magenta/30 text-neon-magenta'
                    : i < 3
                      ? 'bg-neon-cyan/10 border-neon-cyan/20 text-neon-cyan'
                      : 'bg-surface-1 border-surface-3 text-text-secondary'
                }`}
              >
                {i === 0 && '🔥 '}{trait}
              </span>
            ))}
          </div>
        </motion.div>
      )}

      {/* Top Threat Types */}
      {(pulse?.top_threat_types ?? []).length > 0 && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }} className="space-y-2">
          <p className="label-section">TOP THREAT TYPES</p>
          <div className="space-y-1.5">
            {(pulse?.top_threat_types ?? []).slice(0, 5).map((type: string, i: number) => (
              <div key={type} className="flex items-center gap-3 px-3 py-2 arcane-glass">
                <span className="font-mono text-xs text-neon-cyan/40 w-4">{i + 1}.</span>
                <span className="font-mono text-xs text-text-primary">{type}</span>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* You vs Community */}
      {user && user.avg_toxicity_score !== null && pulse && pulse.avg_toxicity_score !== undefined && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="arcane-glass p-4">
          <p className="label-section mb-3">YOU VS COMMUNITY</p>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <p className="font-mono text-xl font-bold text-neon-cyan">{user.avg_toxicity_score}</p>
              <p className="font-mono text-[9px] text-text-secondary uppercase">Your Avg</p>
            </div>
            <div className="text-center">
              <p className="font-mono text-xl font-bold text-text-primary">{pulse.avg_toxicity_score}</p>
              <p className="font-mono text-[9px] text-text-secondary uppercase">Community Avg</p>
            </div>
          </div>
          {user.avg_toxicity_score > pulse.avg_toxicity_score ? (
            <p className="mt-2 text-center font-mono text-[10px] text-neon-magenta">
              Your circle scores higher than average. Stay vigilant.
            </p>
          ) : (
            <p className="mt-2 text-center font-mono text-[10px] text-neon-mint">
              Your circle scores below average. Keep setting boundaries.
            </p>
          )}
        </motion.div>
      )}

      {/* My Insights link (moved from bottom nav) */}
      <Link
        href="/my-insights"
        className="block card-dashed text-center py-4 font-mono text-xs text-neon-cyan/60 active:text-neon-cyan transition-colors touch-active"
      >
        VIEW MY MIRROR &rarr;
      </Link>
    </div>
  );
}
