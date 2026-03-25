'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { RiskLevel } from '@/types/analysis';
import { PersonRow } from '@/types/database';
import { STATUS_LABELS } from '@/lib/constants';

interface PersonListProps {
  people: PersonRow[];
}

function getInitials(name: string) {
  return name.split(/\s+/).map(w => w[0]).join('').toUpperCase().slice(0, 2);
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
      <div className="card-dashed text-center py-10">
        <div className="font-mono text-2xl mb-3 text-white/10">[EMPTY]</div>
        <p className="font-mono text-sm text-white/30 mb-5">NO SUBJECTS IN REGISTRY</p>
        <Link
          href="/analyze"
          className="inline-block card-dashed px-6 py-3 font-mono text-xs uppercase tracking-[0.15em] text-white/60 hover:text-white transition-colors"
        >
          + INITIATE FIRST ANALYSIS
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {deleteError && (
        <div className="p-3 badge-status text-xs">
          {deleteError}
        </div>
      )}
      {people.map((person) => {
        const riskLevel = (person.current_risk_level ?? 'low') as RiskLevel;
        const isHigh = riskLevel === 'high';
        const isConfirming = confirmId === person.id;
        const isDeleting = deletingId === person.id;

        return (
          <div key={person.id} className="relative">
            <Link
              href={`/people/${person.id}`}
              aria-label={`View profile for ${person.name}, risk level ${riskLevel}`}
              className={`flex items-center gap-3 p-4 bg-surface-1 border rounded-lg active:bg-surface-2 transition-all touch-active min-h-[72px] ${
                isConfirming ? 'border-badge-pink/30' : 'border-surface-3'
              }`}
            >
              {/* Portrait placeholder */}
              <div className="relative shrink-0">
                <div className={`w-14 h-14 rounded-lg bg-surface-2 flex items-center justify-center font-mono text-lg font-bold text-white/20 ${isHigh ? 'border border-badge-pink/30' : ''}`}>
                  {getInitials(person.name)}
                </div>
                {isHigh && (
                  <span className="absolute -top-2 -right-2 badge-status text-[8px] px-1.5 py-0.5 rotate-6">
                    HIGH RISK
                  </span>
                )}
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <p className="font-mono text-sm font-bold text-white uppercase truncate">
                  {person.name.toUpperCase().replace(/\s/g, '_')}
                </p>
                <p className="font-mono text-[10px] text-white/30 uppercase mt-0.5">
                  {person.relationship ?? 'UNKNOWN'} &middot; {person.analysis_count} report{person.analysis_count !== 1 ? 's' : ''}
                </p>
                <div className="flex items-center gap-2 mt-1.5">
                  <span className="font-mono text-[10px] bg-white/5 border border-white/10 rounded px-1.5 py-0.5 text-white/50">
                    TOX: {person.current_toxicity_score?.toFixed(1) ?? '?'}
                  </span>
                  <span className={`font-mono text-[10px] rounded px-1.5 py-0.5 ${
                    isHigh ? 'badge-status' : 'bg-white/5 text-white/40'
                  }`}>
                    {STATUS_LABELS[riskLevel]}
                  </span>
                </div>
              </div>

              {/* Delete controls */}
              <div className="flex items-center gap-1 shrink-0">
                {isConfirming && (
                  <button
                    type="button"
                    onClick={(e) => handleDelete(e, person)}
                    disabled={isDeleting}
                    aria-label={`Confirm delete ${person.name}`}
                    className="px-2 py-1 rounded-sm font-mono text-[10px] text-white bg-white/10 border border-white/20 active:bg-white/20 transition-colors"
                  >
                    {isDeleting ? '...' : 'Confirm?'}
                  </button>
                )}
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
                  className={`w-8 h-8 flex items-center justify-center rounded-lg font-mono text-xs transition-colors touch-active ${
                    isConfirming ? 'text-white/50' : 'text-white/15 active:text-white/40'
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
