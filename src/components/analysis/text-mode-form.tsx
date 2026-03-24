'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { RELATIONSHIP_OPTIONS } from '@/lib/constants';
import { FormInput, FormTextarea, FormSelect } from '@/components/ui/form-input';
import { ErrorAlert } from '@/components/ui/error-alert';
import { Spinner } from '@/components/ui/spinner';

export function TextModeForm() {
  const [name, setName] = useState('');
  const [relationship, setRelationship] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, relationship: relationship || null, description }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Analysis failed');
      }

      const data = await response.json();
      router.push(`/people/${data.personId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <p className="text-sm text-white/40 font-mono">
        Describe the subject. The more detail, the sharper the profile.
      </p>

      {error && <ErrorAlert message={error} />}

      <FormInput
        label="Subject Name"
        id="text-subject-name"
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Who are we analyzing?"
        required
      />

      <FormSelect
        label="Relationship"
        id="text-relationship"
        value={relationship}
        onChange={(e) => setRelationship(e.target.value)}
      >
        <option value="">Select relationship...</option>
        {RELATIONSHIP_OPTIONS.map((opt) => (
          <option key={opt} value={opt.toLowerCase()}>{opt}</option>
        ))}
      </FormSelect>

      <FormTextarea
        label="Behavioral Description"
        id="text-description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        rows={8}
        placeholder="Describe their behavior, specific incidents, how they make you feel..."
        required
        minLength={10}
      />

      <button
        type="submit"
        disabled={loading || !name || !description || description.length < 10}
        className="w-full py-4 bg-white text-black font-bold rounded-xl font-mono text-sm tracking-wider active:bg-white/90 transition-all disabled:opacity-30 disabled:cursor-not-allowed min-h-[52px] touch-active"
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <Spinner />
            RUNNING ANALYSIS...
          </span>
        ) : 'INITIATE THREAT ANALYSIS →'}
      </button>

      {loading && (
        <div className="text-center font-mono text-xs text-white/30 space-y-1">
          <p>▸ Scanning behavioral patterns...</p>
          <p>▸ Cross-referencing manipulation frameworks...</p>
          <p>▸ Generating threat profile...</p>
        </div>
      )}
    </form>
  );
}
