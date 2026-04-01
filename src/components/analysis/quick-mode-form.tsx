'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { track } from '@vercel/analytics';
import { Spinner } from '@/components/ui/spinner';
import { ErrorAlert } from '@/components/ui/error-alert';

export interface QuickResult {
  verdict: 'RED_FLAG' | 'YELLOW_FLAG' | 'GREEN_FLAG';
  explanation: string;
  headline: string;
  pattern_name: string;
  score: number;
}

interface QuickModeFormProps {
  onResult?: (result: QuickResult) => void;
}

import { VERDICT_STYLES } from './verdict-styles';

export function QuickModeForm({ onResult }: QuickModeFormProps) {
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<QuickResult | null>(null);
  const hasFocused = useRef(false);
  const hasSubmitted = useRef(false);
  const descriptionRef = useRef('');

  // Keep ref in sync for abandon detection
  useEffect(() => { descriptionRef.current = description; }, [description]);

  // Track form abandonment (typed 5+ chars but left without submitting)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'hidden' && !hasSubmitted.current && descriptionRef.current.trim().length >= 5) {
        track('quick_form_abandoned', { chars_typed: descriptionRef.current.length });
      }
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);

  const handleFocus = useCallback(() => {
    if (!hasFocused.current) {
      hasFocused.current = true;
      track('quick_form_focused');
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!description.trim() || description.trim().length < 5) return;

    setError('');
    setLoading(true);
    setResult(null);
    hasSubmitted.current = true;
    track('try_analysis_started', { mode: 'quick' });

    try {
      const response = await fetch('/api/quick-assess', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: description.trim() }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Assessment failed');
      }

      const data = await response.json();
      setResult(data.result);
      track('try_analysis_completed', { mode: 'quick', verdict: data.result.verdict });
      onResult?.(data.result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setDescription('');
  };

  if (result) {
    const style = VERDICT_STYLES[result.verdict];
    return (
      <div className="space-y-4">
        {/* Verdict card */}
        <div className={`${style.bg} border ${style.border} rounded-xl p-6 text-center space-y-4`}>
          <p className={`font-mono text-2xl font-black uppercase tracking-wider ${style.text} ${style.glow}`}>
            {style.label}
          </p>
          <p className="font-mono text-lg font-bold text-text-primary uppercase">
            &ldquo;{result.headline}&rdquo;
          </p>
          <p className="font-mono text-xs text-text-secondary uppercase tracking-wider">
            Pattern: {result.pattern_name}
          </p>
          <p className="font-mono text-sm text-text-primary leading-relaxed">
            {result.explanation}
          </p>
          <div className="flex items-center justify-center gap-2">
            <span className="font-mono text-xs text-text-secondary">Score:</span>
            <span className={`font-mono text-xl font-bold ${style.text}`}>
              {result.score.toFixed(1)}/10
            </span>
          </div>
        </div>

        {/* Upsell — full threat profile */}
        <div className="arcane-glass p-5 text-center space-y-3">
          <p className="font-mono text-sm text-text-primary font-bold">
            Want the full threat profile?
          </p>
          <p className="text-xs text-text-secondary">
            Sign up to get detailed trait breakdowns, protection strategies, and track patterns over time.
          </p>
          <Link
            href="/signup"
            onClick={() => track('try_signup_clicked', { source: 'quick_result' })}
            className="inline-block px-8 py-3.5 bg-neon-cyan text-surface-0 font-bold rounded-xl font-mono text-sm tracking-wider active:bg-neon-cyan/90 transition-all min-h-[48px] touch-active"
          >
            SIGN UP FREE
          </Link>
        </div>

        {/* Actions */}
        <button
          type="button"
          onClick={handleReset}
          className="w-full py-3.5 border border-neon-cyan/[0.08] rounded-xl font-mono text-xs text-text-secondary active:bg-hover transition-colors min-h-[48px] touch-active focus-visible:outline focus-visible:outline-2 focus-visible:outline-neon-cyan/60"
        >
          ASSESS ANOTHER
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="quick-description" className="label-section mb-2 block">WHAT HAPPENED?</label>
        <textarea
          id="quick-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          onFocus={handleFocus}
          placeholder='e.g. "He said I was overreacting when I caught him lying"'
          className="w-full arcane-glass rounded-xl px-4 py-3 font-mono text-sm text-text-primary placeholder:text-text-secondary/40 min-h-[100px] resize-none focus:border-neon-cyan/40 focus:outline-none transition-colors"
          maxLength={500}
          disabled={loading}
        />
        <p className="mt-1 text-right font-mono text-[10px] text-text-secondary/40">
          {description.length}/500
        </p>
      </div>

      {error && <ErrorAlert message={error} />}

      <button
        type="submit"
        disabled={loading || description.trim().length < 5}
        className="w-full py-4 bg-neon-cyan text-surface-0 font-bold rounded-xl font-mono text-sm tracking-wider active:opacity-90 transition-all min-h-[52px] touch-active disabled:opacity-30"
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <Spinner />
            <span className="font-mono text-xs">&gt;&gt; Assessing...</span>
          </span>
        ) : (
          'IS THIS TOXIC?'
        )}
      </button>
    </form>
  );
}
