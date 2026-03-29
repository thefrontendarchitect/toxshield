'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { RELATIONSHIP_OPTIONS } from '@/lib/constants';

interface PersonHeaderProps {
  personId: string;
  personName: string;
  relationship: string | null;
}

export function PersonHeader({ personId, personName, relationship: initialRelationship }: PersonHeaderProps) {
  const router = useRouter();
  const [editing, setEditing] = useState(false);
  const [relationship, setRelationship] = useState(initialRelationship);
  const [saving, setSaving] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const handleChange = async (value: string) => {
    const newRelationship = value || null;
    setRelationship(newRelationship);
    setEditing(false);
    setSaving(true);

    try {
      const res = await fetch(`/api/people/${personId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ relationship: newRelationship }),
      });

      if (!res.ok) {
        setRelationship(initialRelationship);
      }
    } catch {
      setRelationship(initialRelationship);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!confirmDelete) {
      setConfirmDelete(true);
      return;
    }

    setDeleting(true);
    try {
      const res = await fetch(`/api/people/${personId}`, { method: 'DELETE' });
      if (res.ok) {
        router.push('/people');
      } else {
        setConfirmDelete(false);
        setDeleting(false);
      }
    } catch {
      setConfirmDelete(false);
      setDeleting(false);
    }
  };

  return (
    <div className="space-y-3 mb-5">
      <div className="flex items-center gap-2">
        <Link
          href={`/people/${personId}/add-info`}
          className="flex-1 py-3 card-dashed font-mono text-[10px] uppercase tracking-[0.15em] text-text-secondary active:bg-surface-2 transition-colors text-center min-h-[44px] flex items-center justify-center touch-active"
        >
          + ADD INTEL
        </Link>
        <Link
          href={`/people/${personId}/share`}
          className="flex-1 py-3 bg-neon-cyan text-surface-0 font-bold rounded-lg font-mono text-[10px] uppercase tracking-[0.15em] active:bg-neon-cyan/90 transition-colors text-center min-h-[44px] flex items-center justify-center touch-active"
        >
          SHARE REPORT
        </Link>
      </div>

      <div className="flex items-center justify-between">
        {editing ? (
          <select
            aria-label="Relationship type"
            autoFocus
            value={relationship ?? ''}
            onChange={(e) => handleChange(e.target.value)}
            onBlur={() => setEditing(false)}
            className="w-full py-2 bg-transparent border-b border-neon-cyan/20 font-mono text-xs text-text-primary focus:outline-none focus:border-neon-cyan/40 transition-colors appearance-none"
          >
            <option value="">No relationship</option>
            {RELATIONSHIP_OPTIONS.map((opt) => (
              <option key={opt} value={opt.toLowerCase()}>{opt}</option>
            ))}
          </select>
        ) : (
          <button
            type="button"
            aria-label={`Edit relationship${relationship ? `: ${relationship}` : ''}`}
            onClick={() => setEditing(true)}
            disabled={saving}
            className="flex items-center gap-1.5 py-1.5 font-mono text-[10px] uppercase tracking-[0.15em] transition-colors active:bg-neon-cyan/5 touch-active rounded"
          >
            <span className={relationship ? 'text-text-secondary' : 'text-text-secondary italic'}>
              {saving ? 'SAVING...' : relationship?.toUpperCase() ?? 'SET RELATIONSHIP'}
            </span>
            <span className="text-text-secondary text-[10px]">&#9998;</span>
          </button>
        )}

        {!editing && (
          <button
            type="button"
            onClick={handleDelete}
            onBlur={() => { if (!deleting) setConfirmDelete(false); }}
            disabled={deleting}
            aria-label={
              deleting ? 'Deleting...' :
              confirmDelete ? `Confirm delete ${personName}` :
              `Delete ${personName}`
            }
            className={`px-3 py-2 rounded-sm font-mono text-[10px] uppercase tracking-wider transition-colors min-h-[44px] touch-active ${
              confirmDelete
                ? 'badge-status'
                : 'text-text-secondary active:bg-neon-cyan/5'
            }`}
          >
            {deleting ? 'DELETING...' : confirmDelete ? `DELETE ${personName.toUpperCase()}?` : 'DELETE'}
          </button>
        )}
      </div>
    </div>
  );
}
