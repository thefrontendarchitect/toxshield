import { RiskLevel } from '@/types/analysis';

export function scoreToRiskLevel(score: number): RiskLevel {
  if (score < 4) return 'low';
  if (score < 7) return 'moderate';
  return 'high';
}

export function calculateEnvironmentHealth(
  people: Array<{ current_toxicity_score: number | null; current_risk_level: string | null }>
): number {
  if (people.length === 0) return 100;

  const totalToxicity = people.reduce(
    (sum, p) => sum + (p.current_toxicity_score ?? 0),
    0
  );
  const maxPossibleToxicity = people.length * 10;
  const toxicityPercentage = totalToxicity / maxPossibleToxicity;

  // Additional penalty for high-risk people
  const highRiskCount = people.filter(
    (p) => p.current_risk_level === 'high'
  ).length;
  const highRiskPenalty = highRiskCount * 0.05;

  const health = Math.max(
    0,
    Math.round((1 - toxicityPercentage - highRiskPenalty) * 100)
  );
  return health;
}
