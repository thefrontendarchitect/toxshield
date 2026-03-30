-- Add Razorpay support to purchases table
ALTER TABLE purchases
  ADD COLUMN payment_gateway TEXT NOT NULL DEFAULT 'stripe' CHECK (payment_gateway IN ('stripe', 'razorpay')),
  ADD COLUMN razorpay_order_id TEXT,
  ADD COLUMN razorpay_payment_id TEXT;

CREATE INDEX idx_purchases_razorpay ON purchases(razorpay_order_id);
