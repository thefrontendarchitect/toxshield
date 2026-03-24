-- Add 'slack_chat' to the input_type CHECK constraint
ALTER TABLE inputs DROP CONSTRAINT IF EXISTS inputs_input_type_check;
ALTER TABLE inputs ADD CONSTRAINT inputs_input_type_check CHECK (input_type IN (
  'text_description', 'audio_transcription', 'whatsapp_chat',
  'slack_chat', 'email', 'sms', 'incident'
));
