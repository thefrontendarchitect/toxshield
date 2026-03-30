import { PACKS, type PackType } from '@/lib/packs';
import { createClient as createAdminClient } from '@supabase/supabase-js';
import { NextResponse } from 'next/server';
import crypto from 'crypto';

function getAdminSupabase() {
  return createAdminClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!,
  );
}

export async function POST(request: Request) {
  const body = await request.text();
  const sig = request.headers.get('x-razorpay-signature');

  if (!sig || !process.env.RAZORPAY_WEBHOOK_SECRET) {
    return NextResponse.json({ error: 'Missing signature or config' }, { status: 400 });
  }

  // Verify webhook signature
  const expectedSig = crypto
    .createHmac('sha256', process.env.RAZORPAY_WEBHOOK_SECRET)
    .update(body)
    .digest('hex');

  if (!crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(expectedSig))) {
    return NextResponse.json({ error: 'Invalid signature' }, { status: 400 });
  }

  let event;
  try {
    event = JSON.parse(body);
  } catch {
    return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 });
  }
  const supabase = getAdminSupabase();

  if (event.event === 'payment.captured') {
    const payment = event.payload.payment.entity;
    const orderId = payment.order_id;

    if (!orderId) {
      return NextResponse.json({ received: true });
    }

    // Find the purchase by order ID
    const { data: purchase } = await supabase
      .from('purchases')
      .select('id, pack_type, status')
      .eq('razorpay_order_id', orderId)
      .maybeSingle();

    if (!purchase || purchase.status === 'completed') {
      return NextResponse.json({ received: true });
    }

    const pack = PACKS[purchase.pack_type as PackType];
    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + pack.duration_days);

    const { error: updateError } = await supabase
      .from('purchases')
      .update({
        status: 'completed',
        razorpay_payment_id: payment.id,
        expires_at: expiresAt.toISOString(),
      })
      .eq('id', purchase.id);

    if (updateError) {
      console.error('Failed to activate purchase via webhook:', updateError);
    }
  }

  if (event.event === 'payment.failed') {
    const payment = event.payload.payment.entity;
    const orderId = payment.order_id;

    if (orderId) {
      const { error: failError } = await supabase
        .from('purchases')
        .update({ status: 'failed' })
        .eq('razorpay_order_id', orderId)
        .eq('status', 'pending');

      if (failError) {
        console.error('Failed to mark purchase as failed via webhook:', failError);
      }
    }
  }

  return NextResponse.json({ received: true });
}
