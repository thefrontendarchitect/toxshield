import { TraitSeverity, RiskLevel } from '@/types/analysis';

// Monochrome Brutalist: severity/risk expressed through typography + opacity, not color

export const SEVERITY_STYLES: Record<TraitSeverity, string> = {
  low: 'opacity-40 font-normal',
  moderate: 'opacity-70 font-medium',
  high: 'opacity-100 font-bold',
  critical: 'opacity-100 font-black uppercase tracking-widest',
};

export const SEVERITY_BG: Record<TraitSeverity, string> = {
  low: 'bg-white/5 border-white/10',
  moderate: 'bg-white/8 border-white/15',
  high: 'bg-white/12 border-white/25',
  critical: 'bg-white/20 border-white/40',
};

export const SEVERITY_SYMBOLS: Record<TraitSeverity, string> = {
  low: '○',
  moderate: '◐',
  high: '●',
  critical: '◉',
};

export const RISK_STYLES: Record<RiskLevel, string> = {
  low: 'opacity-40 font-light',
  moderate: 'opacity-70 font-medium',
  high: 'opacity-100 font-bold',
};

export const RISK_BG: Record<RiskLevel, string> = {
  low: 'border-white/20 bg-transparent',
  moderate: 'border-white/40 bg-white/5',
  high: 'border-white bg-white',
};

// Legacy exports for backward compatibility
export const SEVERITY_COLORS: Record<TraitSeverity, string> = {
  low: 'text-white/40',
  moderate: 'text-white/70',
  high: 'text-white',
  critical: 'text-white',
};

export const SEVERITY_BG_COLORS: Record<TraitSeverity, string> = {
  low: 'bg-white/5 border-white/10',
  moderate: 'bg-white/8 border-white/15',
  high: 'bg-white/12 border-white/25',
  critical: 'bg-white/20 border-white/40',
};

export const RISK_COLORS: Record<RiskLevel, string> = {
  low: 'text-white/40',
  moderate: 'text-white/70',
  high: 'text-white',
};

export const RISK_BG_COLORS: Record<RiskLevel, string> = {
  low: 'bg-white/5 border-white/20',
  moderate: 'bg-white/8 border-white/40',
  high: 'bg-white/15 border-white/60',
};

export const RISK_LABELS: Record<RiskLevel, string> = {
  low: 'LOW RISK',
  moderate: 'MODERATE RISK',
  high: 'HIGH RISK',
};

export const RELATIONSHIP_OPTIONS = [
  'Partner',
  'Ex-Partner',
  'Friend',
  'Best Friend',
  'Family Member',
  'Parent',
  'Sibling',
  'Boss',
  'Coworker',
  'Roommate',
  'Neighbor',
  'Acquaintance',
  'Other',
] as const;

export const SCORE_TO_RISK = (score: number): RiskLevel => {
  if (score < 4) return 'low';
  if (score < 7) return 'moderate';
  return 'high';
};
