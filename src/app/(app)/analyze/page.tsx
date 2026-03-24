'use client';

import { useState } from 'react';
import { TextModeForm } from '@/components/analysis/text-mode-form';
import { ChatModeForm } from '@/components/analysis/chat-mode-form';

type Mode = 'text' | 'chat';

export default function AnalyzePage() {
  const [mode, setMode] = useState<Mode>('text');

  return (
    <div>
      {/* Mode tabs */}
      <div className="flex items-center gap-1 mb-6 bg-white/5 rounded-xl p-1">
        {(['text', 'chat'] as Mode[]).map((m) => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className={`flex-1 py-2.5 rounded-lg font-mono text-xs tracking-wider transition-all min-h-[40px] ${
              mode === m
                ? 'bg-white text-black font-bold'
                : 'text-white/40 active:bg-white/10'
            }`}
          >
            {m === 'text' ? 'DESCRIBE' : 'WHATSAPP'}
          </button>
        ))}
      </div>

      {mode === 'text' ? <TextModeForm /> : <ChatModeForm />}
    </div>
  );
}
