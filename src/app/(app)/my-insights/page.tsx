import { createClient } from '@/lib/supabase/server';
import { redirect } from 'next/navigation';
import { AnalysisRow } from '@/types/database';
import { UserInsight, UserPattern } from '@/types/analysis';
import { InsightsTimeline } from '@/components/insights/insights-timeline';
import { InsightsSummary } from '@/components/insights/insights-summary';
import Link from 'next/link';

interface AggregatedInsights {
  totalAnalyses: number;
  boundaryBreakdown: { strong: number; developing: number; weak: number };
  allPatterns: Array<UserPattern & { personName: string; date: string }>;
  allGrowthAreas: Array<{ area: string; count: number }>;
  timeline: Array<{
    personName: string;
    personId: string;
    date: string;
    overallTone: string;
    communicationStyle: string;
    boundaryAwareness: 'strong' | 'developing' | 'weak';
  }>;
  latestInsight: UserInsight | null;
}

function aggregateInsights(
  analyses: Array<AnalysisRow & { person_name: string }>
): AggregatedInsights {
  const withInsights = analyses.filter((a) => a.user_insight);

  const boundaryBreakdown = { strong: 0, developing: 0, weak: 0 };
  const growthMap = new Map<string, number>();
  const allPatterns: AggregatedInsights['allPatterns'] = [];
  const timeline: AggregatedInsights['timeline'] = [];

  for (const a of withInsights) {
    const insight = a.user_insight as UserInsight;

    boundaryBreakdown[insight.boundary_awareness]++;

    for (const area of insight.growth_areas) {
      const normalized = area.toLowerCase().trim();
      growthMap.set(normalized, (growthMap.get(normalized) ?? 0) + 1);
    }

    for (const pattern of insight.detected_patterns) {
      allPatterns.push({
        ...pattern,
        personName: a.person_name,
        date: a.created_at,
      });
    }

    timeline.push({
      personName: a.person_name,
      personId: a.person_id,
      date: a.created_at,
      overallTone: insight.overall_tone,
      communicationStyle: insight.communication_style,
      boundaryAwareness: insight.boundary_awareness,
    });
  }

  const allGrowthAreas = Array.from(growthMap.entries())
    .map(([area, count]) => ({ area, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 8);

  return {
    totalAnalyses: withInsights.length,
    boundaryBreakdown,
    allPatterns: allPatterns.slice(0, 20),
    allGrowthAreas,
    timeline: timeline.reverse(),
    latestInsight: withInsights.length > 0
      ? (withInsights[0].user_insight as UserInsight)
      : null,
  };
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
