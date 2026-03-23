-- Inputs table: raw data feeding each analysis
CREATE TABLE inputs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  analysis_id UUID REFERENCES analyses(id) ON DELETE CASCADE,
  person_id UUID NOT NULL REFERENCES people(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,

  input_type TEXT NOT NULL CHECK (input_type IN (
    'text_description', 'audio_transcription',
    'whatsapp_chat', 'email', 'sms', 'incident'
  )),
  content TEXT NOT NULL,
  raw_file_url TEXT,             -- Supabase Storage URL if file was uploaded
  metadata JSONB,                -- Parser-specific metadata

  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_inputs_person_id ON inputs(person_id);
CREATE INDEX idx_inputs_analysis_id ON inputs(analysis_id);
