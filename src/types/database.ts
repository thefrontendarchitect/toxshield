import { InputType, RiskLevel, ToxicTrait, ProtectionStrategy, SelfReflection, UserInsight } from './analysis';

export interface Profile {
  id: string;
  display_name: string | null;
  avatar_url: string | null;
  tier: 'free' | 'pro' | 'unlimited';
  referral_code: string | null;
  created_at: string;
  updated_at: string;
}

export interface PersonRow {
  id: string;
  user_id: string;
  name: string;
  relationship: string | null;
  current_toxicity_score: number | null;
  current_risk_level: RiskLevel | null;
  is_toxic: boolean;
  analysis_count: number;
  current_threat_type: string | null;
  created_at: string;
  updated_at: string;
}

export type MatchedPerson = Pick<PersonRow, 'id' | 'name' | 'relationship' | 'analysis_count'>;

export interface AnalysisRow {
  id: string;
  person_id: string;
  user_id: string;
  toxicity_score: number;
  risk_level: 'low' | 'moderate' | 'high';
  is_toxic: boolean;
  detected_traits: ToxicTrait[];
  pattern_analysis: string;
  protection_strategies: ProtectionStrategy[];
  self_reflection: SelfReflection | null;
  headline: string;
  tagline: string;
  threat_type: string | null;
  user_insight: UserInsight | null;
  input_summary: string | null;
  model_used: string | null;
  prompt_tokens: number | null;
  completion_tokens: number | null;
  created_at: string;
}

export interface InputRow {
  id: string;
  analysis_id: string | null;
  person_id: string;
  user_id: string;
  input_type: InputType;
  content: string;
  raw_file_url: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
}

export interface StreakRow {
  id: string;
  user_id: string;
  current_streak: number;
  longest_streak: number;
  last_activity_date: string | null;
  streak_freezes: number;
  updated_at: string;
}

export interface BadgeDefinition {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  threshold: number | null;
}

export interface UserBadgeRow {
  id: string;
  user_id: string;
  badge_id: string;
  earned_at: string;
}

export interface HealthCheckinRow {
  id: string;
  user_id: string;
  mood: number;
  note: string | null;
  checked_in_at: string;
  created_at: string;
}

export interface UsageTrackingRow {
  id: string;
  user_id: string;
  period_start: string;
  analyses_used: number;
  bonus_analyses: number;
  updated_at: string;
}

export interface ReferralRow {
  id: string;
  referrer_id: string;
  referred_id: string | null;
  referral_code: string;
  status: 'pending' | 'completed' | 'expired';
  bonus_granted: boolean;
  created_at: string;
  completed_at: string | null;
}

export interface PurchaseRow {
  id: string;
  user_id: string;
  pack_type: 'daily_boost' | 'weekly_intel' | 'monthly_pro';
  payment_gateway: 'stripe' | 'razorpay';
  stripe_session_id: string | null;
  stripe_payment_intent: string | null;
  razorpay_order_id: string | null;
  razorpay_payment_id: string | null;
  status: 'pending' | 'completed' | 'failed' | 'refunded' | 'expired';
  analyses_granted: number;
  analyses_remaining: number;
  expires_at: string;
  created_at: string;
  updated_at: string;
}

export interface PurchaseStatus {
  status: 'pending' | 'completed' | 'failed';
  pack_type: PurchaseRow['pack_type'];
  analyses_remaining: number;
  analyses_granted: number;
  expires_at: string;
}

export interface ActivePackData {
  active: true;
  pack_type: PurchaseRow['pack_type'];
  analyses_remaining: number;
  analyses_granted: number;
  expires_at: string;
}

// Supabase Database type definition (v2 format)
export interface Database {
  public: {
    Tables: {
      profiles: {
        Row: Profile;
        Insert: Partial<Profile> & { id: string };
        Update: Partial<Profile>;
        Relationships: [];
      };
      people: {
        Row: PersonRow;
        Insert: Partial<PersonRow> & { user_id: string; name: string };
        Update: Partial<PersonRow>;
        Relationships: [];
      };
      analyses: {
        Row: AnalysisRow;
        Insert: Partial<AnalysisRow> & {
          person_id: string;
          user_id: string;
          toxicity_score: number;
          risk_level: string;
          detected_traits: unknown;
          pattern_analysis: string;
          protection_strategies: unknown;
          headline: string;
          tagline: string;
        };
        Update: Partial<AnalysisRow>;
        Relationships: [];
      };
      inputs: {
        Row: InputRow;
        Insert: Partial<InputRow> & {
          person_id: string;
          user_id: string;
          input_type: string;
          content: string;
        };
        Update: Partial<InputRow>;
        Relationships: [];
      };
    };
    Views: Record<string, never>;
    Functions: Record<string, never>;
    Enums: Record<string, never>;
    CompositeTypes: Record<string, never>;
  };
}
