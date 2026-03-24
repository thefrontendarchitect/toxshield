'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { RISK_STYLES } from '@/lib/constants';
import { RiskLevel } from '@/types/analysis';
import { PersonRow } from '@/types/database';

interface PersonListProps {
  people: PersonRow[];
}

export function PersonList({ people: initialPeople }: PersonListProps) {
  const router = useRouter();
  const [people, setPeople] = useState(initialPeople);
  const [confirmId, setConfirmId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const handleDelete = async (e: React.MouseEvent, person: PersonRow) => {
    e.preventDefault();
    e.stopPropagation();

    if (confirmId !== person.id) {
      setConfirmId(person.id);
      return;
    }

    setDeletingId(person.id);
    setDeleteError(null);
    try {
      const res = await fetch(`/api/people/${person.id}`, { method: 'DELETE' });
      if (res.ok) {
        setPeople((prev) => prev.filter((p) => p.id !== person.id));
        router.refresh();
      } else {
        setDeleteError(`Failed to delete ${person.name}`);
      }
    } catch {
      setDeleteError(`Failed to delete ${person.name}`);
    } finally {
      setDeletingId(null);
      setConfirmId(null);
    }
  };

  if (people.length === 0) {
    return (
      <div className="bg-surface border border-white/[0.06] rounded-xl p-10 text-center">
        <div className="text-3xl mb-3 font-mono text-white/15">[EMPTY]</div>
        <p className="text-white/40 font-mono text-sm mb-5">No subjects in your database yet.</p>
        <Link
          href="/analyze"
          className="inline-block px-5 py-3 bg-white text-black font-bold rounded-xl font-mono text-sm min-h-[44px]"
        >
          Run Your First Analysis
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {deleteError && (
        <div className="p-3 bg-white/10 border border-white/30 rounded-xl text-white text-xs font-mono font-bold">
          {deleteError}
        </div>
      )}
      {people.map((person) => {
        const riskLevel = (person.current_risk_level ?? 'low') as RiskLevel;
        const riskStyle = RISK_STYLES[riskLevel];
        const isHigh = riskLevel === 'high';
        const isConfirming = confirmId === person.id;
        const isDeleting = deletingId === person.id;

        return (
          <div key={person.id} className="relative">
            <Link
              href={`/people/${person.id}`}
              aria-label={`View profile for ${person.name}, risk level ${riskLevel}`}
              className={`flex items-center justify-between p-4 bg-surface border rounded-xl active:bg-hover transition-all touch-active min-h-[64px] ${
                isConfirming ? 'border-white/30' : 'border-white/[0.06]'
              }`}
            >
              <div className="flex items-center gap-3 min-w-0 flex-1">
                <div aria-hidden="true" className={`w-11 h-11 rounded-full flex items-center justify-center font-mono text-sm font-bold border border-white/20 text-white shrink-0 ${riskStyle} ${isHigh ? 'glow-subtle' : ''}`}>
                  {person.current_toxicity_score?.toFixed(1) ?? '—'}
                </div>
                <div className="min-w-0">
                  <p className="font-mono text-sm font-bold text-white truncate">{person.name}</p>
                  <div className="flex items-center gap-1.5 mt-0.5 flex-wrap">
                    <span className="text-xs text-white/30">{person.relationship ?? 'Unknown'}</span>
                    <span className="text-white/15 text-xs">·</span>
                    <span className={`text-xs font-mono uppercase text-white ${riskStyle}`}>{riskLevel}</span>
                    <span className="text-white/15 text-xs">·</span>
                    <span className="text-xs text-white/30">{person.analysis_count} report{person.analysis_count !== 1 ? 's' : ''}</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 shrink-0 ml-2">
                {isConfirming ? (
                  <button
                    type="button"
                    onClick={(e) => handleDelete(e, person)}
                    disabled={isDeleting}
                    aria-label={`Confirm delete ${person.name}`}
                    className="px-2 py-1 rounded font-mono text-xs text-white bg-white/10 border border-white/30 active:bg-white/20 transition-colors touch-active"
                  >
                    {isDeleting ? '...' : 'Confirm?'}
                  </button>
                ) : null}
                <button
                  type="button"
                  onClick={(e) => {
                    if (isConfirming) {
                      e.preventDefault();
                      e.stopPropagation();
                      setConfirmId(null);
                    } else {
                      handleDelete(e, person);
                    }
                  }}
                  className={`w-8 h-8 flex items-center justify-center rounded-lg font-mono text-sm transition-colors touch-active ${
                    isConfirming
                      ? 'text-white/50 active:bg-white/5'
                      : 'text-white/15 active:text-white/40 active:bg-white/5'
                  }`}
                  aria-label={isConfirming ? 'Cancel delete' : `Delete ${person.name}`}
                >
                  {isConfirming ? '←' : '×'}
                </button>
              </div>
            </Link>
          </div>
        );
      })}
    </div>
  );
}
