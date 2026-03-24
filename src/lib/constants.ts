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
