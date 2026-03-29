import { AnalysisRow } from '@/types/database';

export interface WrappedData {
  month: string;
  totalAnalyses: number;
  totalPeopleAnalyzed: number;
  averageToxicityScore: number;
  highestScoringPerson: { name: string; score: number; headline: string; threatType: string | null } | null;
  mostCommonTrait: { name: string; count: number } | null;
  topThreatTypes: string[];
  riskDistribution: { low: number; moderate: number; high: number };
  boundaryTrend: string;
  totalTraitsDetected: number;
}

export function computeWrappedData(
  analyses: (AnalysisRow & { person_name: string })[],
  monthLabel: string
): WrappedData {
  const totalAnalyses = analyses.length;

  // Unique people analyzed
  const uniquePeople = new Set(analyses.map((a) => a.person_id));
  const totalPeopleAnalyzed = uniquePeople.size;

  // Average toxicity
  const averageToxicityScore = totalAnalyses > 0
    ? Number((analyses.reduce((sum, a) => sum + a.toxicity_score, 0) / totalAnalyses).toFixed(1))
    : 0;

  // Highest scoring person
  const sorted = [...analyses].sort((a, b) => b.toxicity_score - a.toxicity_score);
  const highestScoringPerson = sorted.length > 0
    ? {
        name: sorted[0].person_name,
        score: sorted[0].toxicity_score,
        headline: sorted[0].headline,
        threatType: sorted[0].threat_type,
      }
    : null;

  // Most common trait
  const traitCounts = new Map<string, number>();
  let totalTraitsDetected = 0;
  for (const a of analyses) {
    for (const trait of a.detected_traits ?? []) {
      traitCounts.set(trait.name, (traitCounts.get(trait.name) ?? 0) + 1);
      totalTraitsDetected++;
    }
  }
  const sortedTraits = [...traitCounts.entries()].sort((a, b) => b[1] - a[1]);
  const mostCommonTrait = sortedTraits.length > 0
    ? { name: sortedTraits[0][0], count: sortedTraits[0][1] }
    : null;

  // Top threat types
  const threatTypeCounts = new Map<string, number>();
  for (const a of analyses) {
    if (a.threat_type) {
      threatTypeCounts.set(a.threat_type, (threatTypeCounts.get(a.threat_type) ?? 0) + 1);
    }
  }
  const topThreatTypes = [...threatTypeCounts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([type]) => type);

  // Risk distribution
  const riskDistribution = { low: 0, moderate: 0, high: 0 };
  for (const a of analyses) {
    riskDistribution[a.risk_level as keyof typeof riskDistribution]++;
  }

  // Boundary trend from user insights
  const boundaryLevels = analyses
    .map((a) => a.user_insight?.boundary_awareness)
    .filter(Boolean) as string[];
  const strongCount = boundaryLevels.filter((b) => b === 'strong').length;
  const weakCount = boundaryLevels.filter((b) => b === 'weak').length;
  const boundaryTrend = strongCount > weakCount ? 'Strengthening' : weakCount > strongCount ? 'Needs Work' : 'Steady';

  return {
    month: monthLabel,
    totalAnalyses,
    totalPeopleAnalyzed,
    averageToxicityScore,
    highestScoringPerson,
    mostCommonTrait,
    topThreatTypes,
    riskDistribution,
    boundaryTrend,
    totalTraitsDetected,
  };
}
