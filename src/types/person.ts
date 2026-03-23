import { RiskLevel } from './analysis';

export interface Person {
  id: string;
  user_id: string;
  name: string;
  relationship: string | null;
  current_toxicity_score: number | null;
  current_risk_level: RiskLevel | null;
  is_toxic: boolean;
  analysis_count: number;
  created_at: string;
  updated_at: string;
}
