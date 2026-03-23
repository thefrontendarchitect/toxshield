-- Add user_insight JSONB column to analyses table for dual-profile analysis
-- Stores AI-generated insight about the USER's own behavioral patterns
-- Structure: {communication_style, emotional_patterns, boundary_awareness, detected_patterns[], growth_areas[], overall_tone}
ALTER TABLE analyses ADD COLUMN user_insight JSONB;
