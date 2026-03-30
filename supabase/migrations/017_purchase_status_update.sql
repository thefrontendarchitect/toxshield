-- Add 'refunded' and 'expired' to purchase status values
ALTER TABLE purchases DROP CONSTRAINT IF EXISTS purchases_status_check;
ALTER TABLE purchases ADD CONSTRAINT purchases_status_check
  CHECK (status IN ('pending', 'completed', 'failed', 'refunded', 'expired'));

-- Atomic decrement function to prevent race conditions on concurrent analyses
CREATE OR REPLACE FUNCTION decrement_pack_usage(purchase_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE purchases
  SET analyses_remaining = GREATEST(0, analyses_remaining - 1),
      updated_at = NOW()
  WHERE id = purchase_id
    AND analyses_remaining > 0;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
