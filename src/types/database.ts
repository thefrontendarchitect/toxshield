import { InputType, ToxicTrait, ProtectionStrategy, SelfReflection, UserInsight } from './analysis';

export interface Profile {
  id: string;
  display_name: string | null;
  avatar_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface PersonRow {
  id: string;
  user_id: string;
  name: string;
  relationship: string | null;
  current_toxicity_score: number | null;
  current_risk_level: 'low' | 'moderate' | 'high' | null;
  is_toxic: boolean;
  analysis_count: number;
  created_at: string;
  updated_at: string;
}

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
