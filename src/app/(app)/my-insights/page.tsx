import { createClient } from '@/lib/supabase/server';
import { redirect } from 'next/navigation';
import { AnalysisRow } from '@/types/database';
import { InsightsTimeline } from '@/components/insights/insights-timeline';
import { InsightsSummary } from '@/components/insights/insights-summary';
import { aggregateInsights } from '@/lib/utils/insights';
import Link from 'next/link';

function getOverallStatus(breakdown: { strong: number; developing: number; weak: number }) {
  const total = breakdown.strong + breakdown.developing + breakdown.weak;
  if (total === 0) return { label: 'STATUS: UNKNOWN', variant: 'default' as const };
  const weakRatio = breakdown.weak / total;
  if (weakRatio > 0.5) return { label: 'STATUS: CRITICAL', variant: 'critical' as const };
  if (weakRatio > 0.2) return { label: 'STATUS: MONITORED', variant: 'warning' as const };
  return { label: 'STATUS: STABLE', variant: 'stable' as const };
}

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
        {/* Hero */}
        <div className="space-y-3">
          <h1 className="hero-title">MY MIRROR</h1>
          <span className="badge-status inline-block">STATUS: NO DATA</span>
          <p className="text-sm text-white/40 leading-relaxed">
            Reflecting the digital fallout. A forensic reconstruction of your psychological boundaries and exposure patterns.
          </p>
        </div>

        <div className="card-dashed text-center py-10">
          <span className="font-mono text-2xl text-white/10 block mb-3">&#9672;</span>
          <p className="font-mono text-sm text-white/30 mb-1">NO MIRROR DATA</p>
          <p className="font-mono text-[10px] text-white/20 mb-4 uppercase tracking-wider">
            Run an analysis to see your behavioral patterns reflected back.
          </p>
          <Link
            href="/analyze"
            className="inline-block px-5 py-3 bg-white text-surface-0 font-bold rounded-lg font-mono text-xs uppercase tracking-[0.15em] min-h-[44px]"
          >
            + NEW ANALYSIS
          </Link>
        </div>
      </div>
    );
  }

  const status = getOverallStatus(aggregated.boundaryBreakdown);

  return (
    <div className="space-y-6">
      {/* Hero */}
      <div className="space-y-3">
        <h1 className="hero-title">MY MIRROR</h1>
        <span className={`inline-block font-mono text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-sm ${
          status.variant === 'critical' ? 'badge-status' :
          status.variant === 'warning' ? 'bg-white/10 text-white/70' :
          'bg-white/5 text-white/40'
        }`}>
          {status.label}
        </span>
        <p className="text-sm text-white/40 leading-relaxed">
          Reflecting the digital fallout. A forensic reconstruction of your psychological boundaries and exposure patterns over {aggregated.totalAnalyses} analysis{aggregated.totalAnalyses !== 1 ? 'es' : ''}.
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
