'use client';

import { useState } from 'react';
import { TextModeForm } from '@/components/analysis/text-mode-form';
import { ChatModeForm } from '@/components/analysis/chat-mode-form';
import { SlackModeForm } from '@/components/analysis/slack-mode-form';

type Mode = 'text' | 'chat' | 'slack';

const MODE_LABELS: Record<Mode, string> = {
  text: 'DESCRIBE',
  chat: 'WHATSAPP',
  slack: 'SLACK',
};

export default function AnalyzePage() {
  const [mode, setMode] = useState<Mode>('text');

  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <div className="space-y-3">
        <span className="tag-badge">SUBJECT: TOXIC INFLUENCE MAPPING</span>
        <h1 className="hero-title">
          ANALYZE<br />INPUT<span className="cursor-blink">_</span>
        </h1>
        <p className="text-sm text-text-secondary leading-relaxed">
          Deconstruct the behavioral patterns of the target subject. Select your capture medium and input forensic data for real-time de-escalation mapping.
        </p>
      </div>

      {/* Mode tabs */}
      <div role="tablist" className="flex items-center gap-2">
        {(['text', 'chat', 'slack'] as Mode[]).map((m) => (
          <button
            key={m}
            role="tab"
            aria-selected={mode === m}
            onClick={() => setMode(m)}
            className={`px-5 py-2.5 rounded font-mono text-xs uppercase tracking-[0.15em] border transition-all min-h-[40px] ${
              mode === m
                ? 'bg-neon-cyan text-surface-0 font-bold border-neon-cyan'
                : 'bg-surface-2 text-text-secondary border-surface-3 active:bg-surface-3'
            }`}
          >
            {MODE_LABELS[m]}
          </button>
        ))}
      </div>

      {mode === 'text' ? (
        <TextModeForm />
      ) : mode === 'chat' ? (
        <ChatModeForm />
      ) : (
        <SlackModeForm />
      )}
    </div>
  );
}
