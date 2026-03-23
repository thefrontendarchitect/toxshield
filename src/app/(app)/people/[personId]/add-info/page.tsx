'use client';

import { useState, use } from 'react';
import { useRouter } from 'next/navigation';

export default function AddInfoPage({ params }: { params: Promise<{ personId: string }> }) {
  const { personId } = use(params);
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
        body: JSON.stringify({ name: '', relationship: null, description, personId }),
      });
      if (!response.ok) {
        const data = await response.json();
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
      <p className="text-sm text-white/40 font-mono mb-6">
        New information will be combined with all previous data for an updated analysis.
      </p>
      <form onSubmit={handleSubmit} className="space-y-5">
        {error && (
          <div className="p-4 bg-white/10 border border-white/30 rounded-xl text-white text-sm font-mono font-bold">{error}</div>
        )}
        <div>
          <label className="block text-xs text-white/30 font-mono mb-1.5 uppercase tracking-wider">New Information</label>
          <textarea
            value={description} onChange={(e) => setDescription(e.target.value)}
            className="w-full px-4 py-3.5 bg-black border border-white/10 rounded-xl font-mono text-sm text-white placeholder:text-white/15 focus:outline-none focus:border-white/40 focus:ring-1 focus:ring-white/10 transition-colors resize-none"
            rows={8} placeholder="What new behavior have you observed?" required minLength={10}
          />
        </div>
        <button
          type="submit" disabled={loading || description.length < 10}
          className="w-full py-4 bg-white text-black font-bold rounded-xl font-mono text-sm tracking-wider active:bg-white/90 transition-all disabled:opacity-30 disabled:cursor-not-allowed min-h-[52px] touch-active"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="inline-block w-4 h-4 border-2 border-black/20 border-t-black rounded-full animate-spin" />
              UPDATING PROFILE...
            </span>
          ) : 'UPDATE ANALYSIS →'}
        </button>
        <button
          type="button" onClick={() => router.back()}
          className="w-full py-3 font-mono text-xs text-white/30 active:text-white/60 transition-colors min-h-[44px]"
        >
          ← Cancel
        </button>
      </form>
    </div>
  );
}
