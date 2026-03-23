-- People table: the subjects being analyzed
CREATE TABLE people (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  relationship TEXT, -- e.g., "ex-partner", "boss", "friend", "parent", "coworker"

  -- Latest computed values (denormalized for dashboard speed)
  current_toxicity_score DECIMAL(3,1) DEFAULT 0.0 CHECK (current_toxicity_score >= 0 AND current_toxicity_score <= 10),
  current_risk_level TEXT DEFAULT 'low' CHECK (current_risk_level IN ('low', 'moderate', 'high')),
  is_toxic BOOLEAN DEFAULT TRUE,
  analysis_count INTEGER DEFAULT 0,

  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_people_user_id ON people(user_id);

CREATE TRIGGER people_updated_at
  BEFORE UPDATE ON people
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();
