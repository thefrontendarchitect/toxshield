'use client';

import { motion } from 'framer-motion';
import { AnalysisRow } from '@/types/database';
import { ToxicityRing } from './toxicity-ring';
import { RiskBadge } from './risk-badge';
import { TraitList } from './trait-list';
import { PatternAnalysis } from './pattern-analysis';
import { ProtectionStrategies } from './protection-strategies';
import { SelfReflectionCard } from './self-reflection-card';
import { UserInsightCard } from './user-insight-card';
import { RiskLevel } from '@/types/analysis';

interface ThreatProfileProps {
  analysis: AnalysisRow;
  personName: string;
  relationship: string | null;
}

export function ThreatProfile({ analysis, personName, relationship }: ThreatProfileProps) {
  const traits = analysis.detected_traits;
  const strategies = analysis.protection_strategies;
  const selfReflection = analysis.self_reflection;
  const userInsight = analysis.user_insight;

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center space-y-2"
      >
        <p className="text-[14px] text-white/30 font-mono uppercase tracking-[0.2em]">
          {personName}
          {relationship && ` · ${relationship}`}
        </p>
        <h1 className="text-xl font-bold font-mono text-white">
          &ldquo;{analysis.headline}&rdquo;
        </h1>
        <p className="text-xs text-white/40 italic">{analysis.tagline}</p>
      </motion.div>

      {/* Score + Risk Level */}
      <div className="flex flex-col items-center gap-3">
        <ToxicityRing score={analysis.toxicity_score} />
        <RiskBadge level={analysis.risk_level as RiskLevel} />
      </div>

      {/* Analysis content */}
      {!analysis.is_toxic && selfReflection ? (
        <SelfReflectionCard reflection={selfReflection} />
      ) : (
        <>
          <TraitList traits={traits} />
          <PatternAnalysis text={analysis.pattern_analysis} />
          <ProtectionStrategies strategies={strategies} />
        </>
      )}

      {/* User Mirror */}
      {userInsight && (
        <>
          <div className="border-t border-white/[0.06] my-2" />
          <UserInsightCard insight={userInsight} />
        </>
      )}

      {/* Disclaimer */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 2.5 }}
        className="p-4 bg-surface border border-line rounded-xl"
      >
        <p className="text-[14px] text-white/25 font-mono leading-relaxed text-center">
          ToxShield identifies behavioral patterns. It is not a substitute for professional
          counseling. If you are in danger, contact emergency services.
        </p>
      </motion.div>
    </div>
  );
}
