'use client';

import { useState, useCallback } from 'react';
import Link from 'next/link';
import { track } from '@vercel/analytics';
import { Spinner } from '@/components/ui/spinner';
import { QuickModeForm, type QuickResult } from './quick-mode-form';
import { VERDICT_STYLES } from './verdict-styles';

const SCENARIOS = [
  'He said I was overreacting when I caught him lying',
  'She checks my phone every night but won\'t let me see hers',
  'They give me the silent treatment for days when I disagree',
  'He says nobody else would put up with me',
];

export function TapToAnalyze() {
  const [loadingIdx, setLoadingIdx] = useState<number | null>(null);
  const [result, setResult] = useState<QuickResult | null>(null);
  const [resultScenario, setResultScenario] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState('');

  const handleTap = useCallback(async (scenario: string, idx: number) => {
    if (loadingIdx !== null) return;

    setError('');
    setResult(null);
    setLoadingIdx(idx);
    track('tap_scenario_clicked', { scenario: scenario.slice(0, 50), index: idx });

    try {
      const response = await fetch('/api/quick-assess', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: scenario }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Assessment failed');
      }

      const data = await response.json();
      setResult(data.result);
      setResultScenario(scenario);
      track('tap_scenario_result', { verdict: data.result.verdict, score: data.result.score });
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Something went wrong';
      setError(msg);
      track('tap_scenario_error', { error: msg.slice(0, 100), scenario_index: idx });
    } finally {
      setLoadingIdx(null);
    }
  }, [loadingIdx]);

  const handleReset = useCallback(() => {
    setResult(null);
    setResultScenario('');
    setShowForm(false);
  }, []);

  // Show result
  if (result) {
    const style = VERDICT_STYLES[result.verdict];
    const scoreDisplay = typeof result.score === 'number' ? result.score.toFixed(1) : '?';
    return (
      <div className="space-y-4" role="status" aria-live="polite">
        {/* What was assessed */}
        <p className="font-mono text-[10px] text-text-secondary/60 text-center uppercase tracking-[0.15em]">
          &ldquo;{resultScenario}&rdquo;
        </p>

        {/* Verdict card */}
        <div className={`${style.bg} border ${style.border} rounded-xl p-6 text-center space-y-3`}>
          <div className="flex items-center justify-center gap-3">
            <span className={`font-mono text-2xl font-black uppercase tracking-wider ${style.text} ${style.glow}`}>
              {style.label}
            </span>
            <span className={`font-mono text-2xl font-bold ${style.text}`}>
              {scoreDisplay}
            </span>
          </div>
          <p className="font-mono text-base font-bold text-text-primary uppercase">
            &ldquo;{result.headline}&rdquo;
          </p>
          <p className="font-mono text-xs text-text-secondary uppercase tracking-wider">
            Pattern: {result.pattern_name}
          </p>
          <p className="text-sm text-text-secondary leading-relaxed">
            {result.explanation}
          </p>
        </div>

        {/* Upsell */}
        <Link
          href="/signup"
          onClick={() => track('try_signup_clicked', { source: 'tap_result' })}
          className="block w-full py-4 bg-neon-cyan text-surface-0 font-black rounded-xl font-mono text-sm tracking-[0.15em] text-center active:bg-neon-cyan/90 transition-all min-h-[52px] touch-active uppercase focus-visible:outline focus-visible:outline-2 focus-visible:outline-neon-cyan/60"
        >
          Get Full Threat Profile — Free
        </Link>

        <button
          type="button"
          onClick={handleReset}
          className="w-full py-3 border border-neon-cyan/[0.08] rounded-xl font-mono text-xs text-text-secondary active:bg-hover transition-colors min-h-[44px] touch-active focus-visible:outline focus-visible:outline-2 focus-visible:outline-neon-cyan/60"
        >
          TRY ANOTHER
        </button>
      </div>
    );
  }

  // Show custom form
  if (showForm) {
    return (
      <div className="space-y-3">
        <QuickModeForm />
        <button
          type="button"
          onClick={() => setShowForm(false)}
          className="w-full py-2 font-mono text-[10px] text-text-secondary/60 active:text-neon-cyan/60 transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-neon-cyan/60"
        >
          &larr; Back to scenarios
        </button>
      </div>
    );
  }

  // Scenario cards
  return (
    <div className="space-y-3">
      <p className="font-mono text-[10px] text-neon-cyan/80 tracking-[0.25em] uppercase text-center">
        // is_this_toxic? — tap to find out
      </p>

      {SCENARIOS.map((scenario, idx) => (
        <button
          key={scenario}
          onClick={() => handleTap(scenario, idx)}
          disabled={loadingIdx !== null}
          aria-busy={loadingIdx === idx}
          aria-label={loadingIdx === idx ? 'Assessing scenario...' : `Assess: ${scenario}`}
          className={`w-full text-left arcane-glass p-4 rounded-xl transition-all min-h-[52px] touch-active focus-visible:outline focus-visible:outline-2 focus-visible:outline-neon-cyan/60
            ${loadingIdx === idx ? 'border-neon-cyan/40 glow-subtle' : 'active:border-neon-cyan/30'}
            ${loadingIdx !== null && loadingIdx !== idx ? 'opacity-40' : ''}`}
        >
          {loadingIdx === idx ? (
            <span className="flex items-center gap-3">
              <Spinner />
              <span className="font-mono text-xs text-neon-cyan">&gt;&gt; Assessing...</span>
            </span>
          ) : (
            <p className="text-sm text-text-primary leading-relaxed">
              &ldquo;{scenario}&rdquo;
            </p>
          )}
        </button>
      ))}

      {error && (
        <p className="text-xs text-neon-magenta font-mono text-center" role="alert">{error}</p>
      )}

      <button
        type="button"
        onClick={() => {
          setShowForm(true);
          track('tap_type_own_clicked');
        }}
        className="w-full py-3 font-mono text-xs text-neon-cyan/60 active:text-neon-cyan transition-colors min-h-[44px] touch-active focus-visible:outline focus-visible:outline-2 focus-visible:outline-neon-cyan/60"
      >
        Or type your own scenario →
      </button>
    </div>
  );
}
