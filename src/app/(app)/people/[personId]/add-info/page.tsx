'use client';

import { useState, use } from 'react';
import { useRouter } from 'next/navigation';
import { FormTextarea } from '@/components/ui/form-input';
import { ErrorAlert } from '@/components/ui/error-alert';
import { PaywallModal } from '@/components/ui/paywall-modal';
import { Spinner } from '@/components/ui/spinner';

export default function AddInfoPage({ params }: { params: Promise<{ personId: string }> }) {
  const { personId } = use(params);
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [paywall, setPaywall] = useState<{ used: number; limit: number } | null>(null);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: '', relationship: null, description, personId }),
      });
      if (!response.ok) {
        const data = await response.json();
        if (response.status === 402 && data.error === 'FREE_LIMIT_REACHED') {
          setPaywall(data.usage);
          setLoading(false);
          return;
        }
        throw new Error(data.error || 'Analysis failed');
      }
      router.push(`/people/${personId}`);
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="sr-only">Add New Information</h1>
      <p className="text-sm text-text-secondary font-mono mb-6">
        New information will be combined with all previous data for an updated analysis.
      </p>
      <form onSubmit={handleSubmit} className="space-y-5">
        {error && <ErrorAlert message={error} />}

        <FormTextarea
          label="New Information"
          id="add-info-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={8}
          placeholder="What new behavior have you observed?"
          required
          minLength={10}
        />

        <button
          type="submit" disabled={loading || description.length < 10}
          className="w-full py-4 bg-neon-cyan text-surface-0 font-bold rounded-xl font-mono text-sm tracking-wider active:bg-neon-cyan/90 transition-all disabled:opacity-30 disabled:cursor-not-allowed min-h-[52px] touch-active"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <Spinner />
              UPDATING PROFILE...
            </span>
          ) : 'UPDATE ANALYSIS →'}
        </button>
        <button
          type="button" onClick={() => router.back()}
          className="w-full py-3 font-mono text-xs text-text-secondary active:text-text-primary transition-colors min-h-[44px]"
        >
          ← Cancel
        </button>
      </form>

      {paywall && (
        <PaywallModal
          isOpen={!!paywall}
          onClose={() => setPaywall(null)}
          used={paywall.used}
          limit={paywall.limit}
        />
      )}
    </div>
  );
}
