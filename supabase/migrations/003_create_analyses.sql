-- Analyses table: each AI analysis run (supports incremental updates)
CREATE TABLE analyses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  person_id UUID NOT NULL REFERENCES people(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

  -- AI-generated analysis result
  toxicity_score DECIMAL(3,1) NOT NULL CHECK (toxicity_score >= 0 AND toxicity_score <= 10),
  risk_level TEXT NOT NULL CHECK (risk_level IN ('low', 'moderate', 'high')),
  is_toxic BOOLEAN NOT NULL DEFAULT TRUE,

  -- Structured analysis data (JSONB)
  detected_traits JSONB NOT NULL DEFAULT '[]',           -- [{name, severity, description, icon}]
  pattern_analysis TEXT NOT NULL,                         -- 2-3 sentence behavioral summary
  protection_strategies JSONB NOT NULL DEFAULT '[]',     -- [{title, description, priority}]
  self_reflection JSONB,                                  -- When is_toxic=false: {message, suggestions[]}

  -- Witty summary for share cards
  headline TEXT NOT NULL,                                 -- e.g., "Olympic-Level Gaslighter"
  tagline TEXT NOT NULL,                                  -- Short witty one-liner

  -- What input triggered this analysis
  input_summary TEXT,

  -- Model metadata
  model_used TEXT,
  prompt_tokens INTEGER,
  completion_tokens INTEGER,

  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_analyses_person_id ON analyses(person_id);
CREATE INDEX idx_analyses_user_id ON analyses(user_id);
CREATE INDEX idx_analyses_created_at ON analyses(created_at DESC);
