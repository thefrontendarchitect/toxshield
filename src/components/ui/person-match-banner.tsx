'use client';

import { useState } from 'react';
import type { MatchedPerson } from '@/types/database';
import type { InputType } from '@/lib/utils/name-suggestions';

interface PersonMatchBannerProps {
  matchedPerson: MatchedPerson;
  isChecking: boolean;
  isDifferentPerson: boolean;
  suggestedNames: string[];
  selectedName: string | null;
  inputType: InputType;
  relationship?: string | null;
  onMarkDifferent: (inputType: InputType, relationship?: string | null) => void;
  onSelectName: (name: string) => void;
}

export function PersonMatchBanner({
  matchedPerson,
  isChecking,
  isDifferentPerson,
  suggestedNames,
  selectedName,
  inputType,
  relationship,
  onMarkDifferent,
  onSelectName,
}: PersonMatchBannerProps) {
  const [customName, setCustomName] = useState('');

  if (isChecking) {
    return (
      <div className="bg-surface-1 border border-surface-3 rounded-xl p-4 text-center">
        <p className="text-xs text-text-secondary font-mono">Checking records...</p>
      </div>
    );
  }

  if (!matchedPerson) return null;

  // State A: Match found, not marked as different
  if (!isDifferentPerson) {
    return (
      <div className="bg-surface-1 border border-surface-3 rounded-xl p-4 space-y-3">
        <div>
          <p className="text-sm text-text-primary font-mono font-bold">
            {matchedPerson.name.toUpperCase()} already in your records
          </p>
          <p className="text-xs text-text-secondary font-mono mt-1">
            {matchedPerson.analysis_count} {matchedPerson.analysis_count === 1 ? 'analysis' : 'analyses'}
            {matchedPerson.relationship ? ` · ${matchedPerson.relationship}` : ''}
          </p>
          <p className="text-xs text-text-secondary font-mono mt-2">
            New data will be added to their profile.
          </p>
        </div>
        <button
          type="button"
          onClick={() => onMarkDifferent(inputType, relationship)}
          className="text-xs text-text-secondary font-mono underline underline-offset-2 active:text-text-primary transition-colors"
        >
          This is a different {matchedPerson.name}
        </button>
      </div>
    );
  }

  // State B: User says it's a different person — show quirky name picker
  return (
    <div className="bg-surface-1 border border-surface-3 rounded-xl p-4 space-y-3">
      <p className="text-xs text-text-secondary font-mono font-bold uppercase tracking-wider">
        Pick a name to tell them apart
      </p>

      <div className="space-y-1.5" role="group" aria-label="Name suggestions">
        {suggestedNames.map((name) => {
          const isSelected = selectedName === name;
          return (
            <button
              key={name}
              type="button"
              onClick={() => onSelectName(name)}
              aria-pressed={isSelected}
              className={`w-full flex items-center justify-between p-3 rounded-lg border transition-all text-left min-h-[44px] touch-active ${
                isSelected
                  ? 'border-text-primary bg-surface-2'
                  : 'border-surface-3 bg-surface-0 active:bg-surface-2'
              }`}
            >
              <p className={`font-mono text-sm ${isSelected ? 'text-text-primary font-bold' : 'text-text-secondary'}`}>
                {name}
              </p>
              {isSelected && <span className="text-text-primary font-mono text-xs">●</span>}
            </button>
          );
        })}
      </div>

      {/* Custom name input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={customName}
          onChange={(e) => setCustomName(e.target.value)}
          placeholder="Or type a custom name..."
          aria-label="Custom person name"
          className="flex-1 px-3 py-2.5 bg-surface-0 border border-surface-3 rounded-lg font-mono text-sm text-text-primary placeholder:text-text-secondary/30 focus:border-text-secondary focus:outline-none min-h-[44px]"
        />
        {customName.trim() && (
          <button
            type="button"
            onClick={() => {
              onSelectName(customName.trim());
              setCustomName('');
            }}
            className="px-3 py-2.5 bg-text-primary text-surface-0 font-mono text-xs font-bold rounded-lg active:opacity-90 transition-colors min-h-[44px] touch-active"
          >
            USE
          </button>
        )}
      </div>
    </div>
  );
}
