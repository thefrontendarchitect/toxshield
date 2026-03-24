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
    <div>
      <h1 className="sr-only">New Analysis</h1>
      {/* Mode tabs */}
      <div role="tablist" className="flex items-center gap-1 mb-6 bg-white/5 rounded-xl p-1">
        {(['text', 'chat', 'slack'] as Mode[]).map((m) => (
          <button
            key={m}
            role="tab"
            aria-selected={mode === m}
            onClick={() => setMode(m)}
            className={`flex-1 py-2.5 rounded-lg font-mono text-xs tracking-wider transition-all min-h-[40px] ${
              mode === m
                ? 'bg-white text-background font-bold'
                : 'text-white/40 active:bg-white/10'
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
