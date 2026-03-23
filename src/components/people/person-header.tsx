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
          className="flex-1 py-3 border border-white/15 rounded-xl font-mono text-xs text-white active:bg-white/5 transition-colors text-center min-h-[44px] flex items-center justify-center touch-active"
        >
          + Add Intel
        </Link>
        <Link
          href={`/people/${personId}/share`}
          className="flex-1 py-3 bg-white text-black font-bold rounded-xl font-mono text-xs active:bg-white/90 transition-colors text-center min-h-[44px] flex items-center justify-center touch-active"
        >
          Share Report
        </Link>
      </div>

      <div className="flex items-center justify-between">
        {/* Editable relationship */}
        {editing ? (
          <select
            aria-label="Relationship type"
            autoFocus
            value={relationship ?? ''}
            onChange={(e) => handleChange(e.target.value)}
            onBlur={() => setEditing(false)}
            className="w-full px-3 py-2 bg-black border border-white/20 rounded-lg font-mono text-xs text-white focus:outline-none focus:border-white/40 transition-colors appearance-none"
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
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-mono text-xs transition-colors active:bg-white/5 touch-active"
          >
            <span className={relationship ? 'text-white/40' : 'text-white/20 italic'}>
              {saving ? 'Saving...' : relationship ?? 'Set relationship'}
            </span>
            <span className="text-white/15 text-xs">✎</span>
          </button>
        )}

        {/* Delete button */}
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
            className={`px-3 py-2 rounded-lg font-mono text-xs transition-colors min-h-[44px] touch-active ${
              confirmDelete
                ? 'text-white bg-white/10 border border-white/30'
                : 'text-white/25 active:bg-white/5'
            }`}
          >
            {deleting ? 'Deleting...' : confirmDelete ? `Delete ${personName}?` : 'Delete'}
          </button>
        )}
      </div>
    </div>
  );
}
