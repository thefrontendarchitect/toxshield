'use client';

import { useState } from 'react';
import Link from 'next/link';
import { AppHeader } from '@/components/layout/app-header';
import { TextModeForm } from '@/components/analysis/text-mode-form';
import { ChatModeForm } from '@/components/analysis/chat-mode-form';
import { SlackModeForm } from '@/components/analysis/slack-mode-form';
import { ThreatProfile } from '@/components/analysis/threat-profile';
import { RiskBadge } from '@/components/analysis/risk-badge';
import { AnalysisResult, RiskLevel } from '@/types/analysis';
import { AnalysisRow } from '@/types/database';

interface TryEntry {
  id: string;
  name: string;
  relationship: string | null;
  result: AnalysisResult;
  timestamp: Date;
}

type Mode = 'text' | 'chat' | 'slack';

function toAnalysisRow(result: AnalysisResult): AnalysisRow {
  return {
    id: '',
    person_id: '',
    user_id: '',
    toxicity_score: result.toxicity_score,
    risk_level: result.risk_level,
    is_toxic: result.is_toxic,
    detected_traits: result.detected_traits,
    pattern_analysis: result.pattern_analysis,
    protection_strategies: result.protection_strategies,
    self_reflection: result.self_reflection,
    headline: result.headline,
    tagline: result.tagline,
    user_insight: result.user_insight,
    input_summary: null,
    model_used: null,
    prompt_tokens: null,
    completion_tokens: null,
    created_at: new Date().toISOString(),
  };
}

export default function TryPage() {
  const [analyses, setAnalyses] = useState<TryEntry[]>([]);
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const [mode, setMode] = useState<Mode>('text');

  const handleResult = (name: string, relationship: string | null, result: AnalysisResult) => {
    const entry: TryEntry = {
      id: crypto.randomUUID(),
      name,
      relationship,
      result,
      timestamp: new Date(),
    };
    setAnalyses((prev) => [entry, ...prev]);
    setActiveIndex(0);
  };

  const activeEntry = activeIndex !== null ? analyses[activeIndex] : null;

  return (
    <div className="min-h-screen bg-surface-0">
      <AppHeader title="TRY TOXSHIELD" showBackButton />

      <main className="pt-[72px] pb-8 px-4 max-w-lg mx-auto">
        {/* Active result view */}
        {activeEntry ? (
          <div className="space-y-6">
            <ThreatProfile
              analysis={toAnalysisRow(activeEntry.result)}
              personName={activeEntry.name}
              relationship={activeEntry.relationship}
            />

            {/* Sign up CTA */}
            <div className="bg-surface-1 border border-surface-3 rounded-xl p-6 text-center space-y-3">
              <p className="text-sm text-text-secondary font-mono">
                Want to save this analysis?
              </p>
              <p className="text-xs text-text-secondary font-mono">
                Sign up to track patterns over time and build full profiles.
              </p>
              <Link
                href="/signup"
                className="inline-block px-8 py-3.5 bg-foreground text-background font-bold rounded-xl font-mono text-sm tracking-wider active:opacity-90 transition-all min-h-[48px] touch-active"
              >
                SIGN UP FREE
              </Link>
            </div>

            {/* Analyze another */}
            <button
              type="button"
              onClick={() => setActiveIndex(null)}
              aria-label="Start a new analysis"
              className="w-full py-4 border border-surface-3 rounded-xl font-mono text-sm text-text-secondary active:bg-surface-1 transition-colors min-h-[52px] touch-active"
            >
              ANALYZE ANOTHER
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Session history */}
            {analyses.length > 0 && (
              <div className="space-y-2">
                <p className="text-xs text-text-secondary font-mono uppercase tracking-wider">
                  Session History
                </p>
                <div className="space-y-1.5 max-h-[200px] overflow-y-auto">
                  {analyses.map((entry, i) => (
                    <button
                      key={entry.id}
                      type="button"
                      onClick={() => setActiveIndex(i)}
                      aria-label={`View analysis for ${entry.name}`}
                      className="w-full flex items-center justify-between p-3 bg-surface-1 border border-surface-3 rounded-xl active:bg-surface-2 transition-colors min-h-[44px] text-left"
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <span className="font-mono text-sm text-text-primary truncate">
                          {entry.name}
                        </span>
                        <RiskBadge level={entry.result.risk_level as RiskLevel} />
                      </div>
                      <span className="font-mono text-xs text-text-secondary shrink-0 ml-2">
                        {entry.result.toxicity_score.toFixed(1)}/10
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Ephemeral notice */}
            <p className="text-xs text-text-secondary font-mono text-center">
              Results are not saved. Sign up to keep them.
            </p>

            {/* Mode tabs */}
            <div className="flex items-center gap-1 bg-surface-1 rounded-xl p-1">
              {(['text', 'chat', 'slack'] as Mode[]).map((m) => (
                <button
                  type="button"
                  key={m}
                  onClick={() => setMode(m)}
                  className={`flex-1 py-2.5 rounded-lg font-mono text-xs tracking-wider transition-all min-h-[40px] ${
                    mode === m
                      ? 'bg-foreground text-background font-bold'
                      : 'text-text-secondary active:bg-surface-2'
                  }`}
                >
                  {m === 'text' ? 'DESCRIBE' : m === 'chat' ? 'WHATSAPP' : 'SLACK'}
                </button>
              ))}
            </div>

            {/* Form */}
            {mode === 'text' ? (
              <TextModeForm
                apiEndpoint="/api/try-analyze"
                onResult={handleResult}
              />
            ) : mode === 'chat' ? (
              <ChatModeForm
                apiEndpoint="/api/try-analyze"
                onResult={handleResult}
              />
            ) : (
              <SlackModeForm
                apiEndpoint="/api/try-analyze"
                onResult={handleResult}
              />
            )}
          </div>
        )}
      </main>
    </div>
  );
}
