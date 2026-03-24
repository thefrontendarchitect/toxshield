import { AnalysisRow } from '@/types/database';
import { UserInsight, AggregatedInsights } from '@/types/analysis';

export function aggregateInsights(
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
