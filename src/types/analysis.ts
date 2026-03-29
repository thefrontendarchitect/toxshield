export type TraitSeverity = 'low' | 'moderate' | 'high' | 'critical';
export type RiskLevel = 'low' | 'moderate' | 'high';
export type StrategyPriority = 'essential' | 'recommended' | 'optional';
export type InputType = 'text_description' | 'audio_transcription' | 'whatsapp_chat' | 'slack_chat' | 'email' | 'sms' | 'incident';

export interface ToxicTrait {
  name: string;
  severity: TraitSeverity;
  description: string;
  icon: string;
}

export interface ProtectionStrategy {
  title: string;
  description: string;
  priority: StrategyPriority;
}

export interface SelfReflection {
  message: string;
  suggestions: string[];
}

export type InsightSentiment = 'positive' | 'neutral' | 'needs_attention';

export interface UserPattern {
  area: string;
  observation: string;
  sentiment: InsightSentiment;
  icon: string;
}

export interface UserInsight {
  communication_style: string;
  emotional_patterns: string;
  boundary_awareness: 'strong' | 'developing' | 'weak';
  detected_patterns: UserPattern[];
  growth_areas: string[];
  overall_tone: string;
}

export interface AggregatedInsights {
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

export interface AnalysisResult {
  toxicity_score: number;
  risk_level: RiskLevel;
  is_toxic: boolean;
  detected_traits: ToxicTrait[];
  pattern_analysis: string;
  protection_strategies: ProtectionStrategy[];
  self_reflection: SelfReflection | null;
  headline: string;
  tagline: string;
  threat_type: string;
  user_insight: UserInsight;
}
