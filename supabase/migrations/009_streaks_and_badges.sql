-- Streak tracking (one row per user)
CREATE TABLE streaks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  current_streak INTEGER NOT NULL DEFAULT 0,
  longest_streak INTEGER NOT NULL DEFAULT 0,
  last_activity_date DATE,
  streak_freezes INTEGER NOT NULL DEFAULT 1,
  updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(user_id)
);

CREATE INDEX idx_streaks_user_id ON streaks(user_id);

CREATE TRIGGER streaks_updated_at
  BEFORE UPDATE ON streaks
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

ALTER TABLE streaks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own streak"
  ON streaks FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own streak"
  ON streaks FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own streak"
  ON streaks FOR UPDATE USING (auth.uid() = user_id);

-- Badge definitions (public read, admin-managed)
CREATE TABLE badge_definitions (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  icon TEXT NOT NULL,
  category TEXT NOT NULL,
  threshold INTEGER
);

ALTER TABLE badge_definitions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read badge definitions"
  ON badge_definitions FOR SELECT USING (true);

-- Seed badge definitions
INSERT INTO badge_definitions (id, name, description, icon, category, threshold) VALUES
  ('first_analysis', 'First Blood', 'Completed your first analysis', '🎯', 'milestone', 1),
  ('streak_3', 'On a Roll', '3-week analysis streak', '🔥', 'streak', 3),
  ('streak_7', 'Dedicated Agent', '7-week analysis streak', '⚡', 'streak', 7),
  ('streak_12', 'Unstoppable', '12-week analysis streak', '💎', 'streak', 12),
  ('streak_26', 'Half-Year Hawk', '26-week analysis streak', '🦅', 'streak', 26),
  ('streak_52', 'Forensic Legend', '52-week analysis streak', '👑', 'streak', 52),
  ('analyses_5', 'Pattern Seeker', 'Completed 5 analyses', '🔍', 'milestone', 5),
  ('analyses_10', 'Veteran Agent', 'Completed 10 analyses', '🏅', 'milestone', 10),
  ('analyses_25', 'Master Profiler', 'Completed 25 analyses', '🧠', 'milestone', 25),
  ('people_3', 'Inner Circle', 'Tracked 3 people', '📋', 'milestone', 3),
  ('people_5', 'Network Mapper', 'Tracked 5 people', '🗺️', 'milestone', 5),
  ('people_10', 'Intelligence Bureau', 'Tracked 10 people', '🏛️', 'milestone', 10);

-- User earned badges
CREATE TABLE user_badges (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  badge_id TEXT NOT NULL REFERENCES badge_definitions(id),
  earned_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(user_id, badge_id)
);

CREATE INDEX idx_user_badges_user_id ON user_badges(user_id);

ALTER TABLE user_badges ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own badges"
  ON user_badges FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can earn badges"
  ON user_badges FOR INSERT WITH CHECK (auth.uid() = user_id);
