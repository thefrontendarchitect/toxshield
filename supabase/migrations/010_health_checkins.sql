-- Daily mood check-ins for gamified environment health
CREATE TABLE health_checkins (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  mood INTEGER NOT NULL CHECK (mood >= 1 AND mood <= 5),
  note TEXT,
  checked_in_at DATE NOT NULL DEFAULT CURRENT_DATE,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(user_id, checked_in_at)
);

CREATE INDEX idx_health_checkins_user ON health_checkins(user_id, checked_in_at DESC);

ALTER TABLE health_checkins ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own checkins"
  ON health_checkins FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create own checkins"
  ON health_checkins FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own checkins"
  ON health_checkins FOR UPDATE USING (auth.uid() = user_id);
