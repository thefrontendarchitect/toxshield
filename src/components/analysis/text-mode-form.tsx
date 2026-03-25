'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { RELATIONSHIP_OPTIONS } from '@/lib/constants';
import { FormInput, FormTextarea, FormSelect } from '@/components/ui/form-input';
import { ErrorAlert } from '@/components/ui/error-alert';
import { Spinner } from '@/components/ui/spinner';
import { PersonMatchBanner } from '@/components/ui/person-match-banner';
import { usePersonMatch } from '@/hooks/use-person-match';
import { AnalysisResult } from '@/types/analysis';

interface TextModeFormProps {
  apiEndpoint?: string;
  onResult?: (name: string, relationship: string | null, result: AnalysisResult) => void;
}

export function TextModeForm({ apiEndpoint = '/api/analyze', onResult }: TextModeFormProps) {
  const [name, setName] = useState('');
  const [relationship, setRelationship] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();
  const personMatch = usePersonMatch();

  const handleNameBlur = () => {
    if (name.trim() && apiEndpoint === '/api/analyze') {
      personMatch.checkName(name.trim());
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const submitName = personMatch.resolvedName || name;
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: submitName,
          relationship: relationship || null,
          description,
          ...(personMatch.resolvedPersonId && { personId: personMatch.resolvedPersonId }),
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Analysis failed');
      }

      const data = await response.json();

      if (onResult) {
        onResult(name, relationship || null, data.result);
        setName('');
        setRelationship('');
        setDescription('');
        personMatch.reset();
        setLoading(false);
      } else {
        router.push(`/people/${data.personId}`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <p className="label-section mb-1">
        DESCRIBE THE SUBJECT. THE MORE DETAIL, THE SHARPER THE PROFILE.
      </p>

      {error && <ErrorAlert message={error} />}

      <FormInput
        label="Subject Name"
        id="text-subject-name"
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        onBlur={handleNameBlur}
        placeholder="Who are we analyzing?"
        required
      />

      {/* Person match detection */}
      {apiEndpoint === '/api/analyze' && personMatch.matchedPerson && (
        <PersonMatchBanner
          matchedPerson={personMatch.matchedPerson}
          isChecking={personMatch.isChecking}
          isDifferentPerson={personMatch.isDifferentPerson}
          suggestedNames={personMatch.suggestedNames}
          selectedName={personMatch.selectedName}
          inputType="text_description"
          relationship={relationship}
          onMarkDifferent={personMatch.markAsDifferent}
          onSelectName={personMatch.selectAlternateName}
        />
      )}

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
        disabled={loading || !name || !description || description.length < 10 || (personMatch.isDifferentPerson && !personMatch.selectedName)}
        className="w-full py-4 bg-white text-surface-0 font-bold rounded-lg font-mono text-xs uppercase tracking-[0.15em] active:bg-white/90 transition-all disabled:opacity-30 disabled:cursor-not-allowed min-h-[52px] touch-active"
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <Spinner />
            RUNNING ANALYSIS...
          </span>
        ) : 'INITIATE THREAT ANALYSIS \u2192'}
      </button>

      {loading && (
        <div className="text-center font-mono text-[10px] text-white/30 uppercase tracking-wider space-y-1">
          <p>&gt;&gt; Scanning behavioral patterns...</p>
          <p>&gt;&gt; Cross-referencing manipulation frameworks...</p>
          <p>&gt;&gt; Generating threat profile...</p>
        </div>
      )}
    </form>
  );
}
