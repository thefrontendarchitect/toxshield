-- Enable Row Level Security on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE people ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE inputs ENABLE ROW LEVEL SECURITY;

-- Profiles: users can only read/update their own profile
CREATE POLICY "Users can view own profile"
  ON profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE
  USING (auth.uid() = id);

-- People: users can only CRUD their own people
CREATE POLICY "Users can view own people"
  ON people FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create own people"
  ON people FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own people"
  ON people FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own people"
  ON people FOR DELETE
  USING (auth.uid() = user_id);

-- Analyses: users can only CRUD their own analyses
CREATE POLICY "Users can view own analyses"
  ON analyses FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create own analyses"
  ON analyses FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own analyses"
  ON analyses FOR DELETE
  USING (auth.uid() = user_id);

-- Inputs: users can only CRUD their own inputs
CREATE POLICY "Users can view own inputs"
  ON inputs FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create own inputs"
  ON inputs FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own inputs"
  ON inputs FOR DELETE
  USING (auth.uid() = user_id);
