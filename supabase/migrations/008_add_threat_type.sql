-- Add threat_type to analyses (archetype label like "The Puppet Master")
ALTER TABLE analyses ADD COLUMN threat_type TEXT;

-- Denormalize to people for fast dashboard access
ALTER TABLE people ADD COLUMN current_threat_type TEXT;
