import { createClient } from '@/lib/supabase/server';
import { redirect } from 'next/navigation';
import { AnalysisRow } from '@/types/database';
import { InsightsTimeline } from '@/components/insights/insights-timeline';
import { InsightsSummary } from '@/components/insights/insights-summary';
import { aggregateInsights } from '@/lib/utils/insights';
import Link from 'next/link';

export default async function MyInsightsPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect('/login');

  const { data: analyses } = await supabase
    .from('analyses')
    .select('*, people!inner(name)')
    .eq('user_id', user.id)
    .order('created_at', { ascending: false })
    .returns<Array<AnalysisRow & { people: { name: string } }>>();

  const normalizedAnalyses = (analyses ?? []).map((a) => ({
    ...a,
    person_name: a.people?.name ?? 'Unknown',
  }));

  const aggregated = aggregateInsights(normalizedAnalyses);

  if (aggregated.totalAnalyses === 0) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-xs text-white/30 font-mono uppercase tracking-[0.15em] mb-1">
            My Mirror
          </h1>
          <p className="text-lg font-mono font-bold text-white">Your Behavioral Patterns</p>
        </div>

        <div className="bg-surface border border-white/[0.06] rounded-xl p-8 text-center">
          <span className="text-3xl text-white/20 block mb-3">◈</span>
          <p className="text-white/40 font-mono text-sm mb-1">No mirror data yet.</p>
          <p className="text-white/25 text-xs mb-4">
            Run an analysis to see your own behavioral patterns reflected back.
          </p>
          <Link
            href="/analyze"
            className="inline-block px-4 py-3 bg-white text-black font-bold rounded-xl font-mono text-sm min-h-[44px]"
          >
            + New Analysis
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xs text-white/30 font-mono uppercase tracking-[0.15em] mb-1">
          My Mirror
        </h1>
        <p className="text-lg font-mono font-bold text-white">Your Behavioral Patterns</p>
        <p className="text-xs text-white/30 mt-1">
          Aggregated from {aggregated.totalAnalyses} analysis{aggregated.totalAnalyses !== 1 ? 'es' : ''}
        </p>
      </div>

      <InsightsSummary
        latestInsight={aggregated.latestInsight!}
        boundaryBreakdown={aggregated.boundaryBreakdown}
        totalAnalyses={aggregated.totalAnalyses}
        allGrowthAreas={aggregated.allGrowthAreas}
      />

      <InsightsTimeline
        timeline={aggregated.timeline}
        allPatterns={aggregated.allPatterns}
      />
    </div>
  );
}
