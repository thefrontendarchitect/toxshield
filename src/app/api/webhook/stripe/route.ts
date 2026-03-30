import { getStripe } from '@/lib/stripe';
import { PACKS } from '@/lib/packs';
import { createClient as createAdminClient } from '@supabase/supabase-js';
import { NextResponse } from 'next/server';

// Use service role for webhook — no user auth context
function getAdminSupabase() {
  return createAdminClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!,
  );
}

export async function POST(request: Request) {
  const body = await request.text();
  const sig = request.headers.get('stripe-signature');

  if (!sig) {
    return NextResponse.json({ error: 'Missing signature' }, { status: 400 });
  }

  if (!process.env.STRIPE_WEBHOOK_SECRET) {
    console.error('STRIPE_WEBHOOK_SECRET is not configured');
    return NextResponse.json({ error: 'Server misconfiguration' }, { status: 500 });
  }

  let event;
  try {
    event = getStripe().webhooks.constructEvent(body, sig, process.env.STRIPE_WEBHOOK_SECRET);
  } catch (err) {
    console.error('Webhook signature verification failed:', err);
    return NextResponse.json({ error: 'Invalid signature' }, { status: 400 });
  }

  if (event.type === 'checkout.session.completed') {
    const session = event.data.object;
    const userId = session.metadata?.user_id;
    const packType = session.metadata?.pack_type;

    if (!userId || !packType || !(packType in PACKS)) {
      console.error('Invalid webhook metadata:', session.metadata);
      return NextResponse.json({ error: 'Invalid metadata' }, { status: 400 });
    }

    const supabase = getAdminSupabase();

    // Idempotency: skip if already processed
    const { data: existing } = await supabase
      .from('purchases')
      .select('status')
      .eq('stripe_session_id', session.id)
      .maybeSingle();

    if (existing?.status === 'completed') {
      return NextResponse.json({ received: true });
    }

    // Activate the purchase (expires_at was set correctly at checkout time)
    const { error, data } = await supabase
      .from('purchases')
      .update({
        status: 'completed',
        stripe_payment_intent: session.payment_intent,
      })
      .eq('stripe_session_id', session.id)
      .select();

    if (error || !data?.length) {
      console.error('Purchase not found or update failed:', session.id, error);
      return NextResponse.json({ error: 'Purchase activation failed' }, { status: 500 });
    }
  }

  if (event.type === 'charge.refunded') {
    const charge = event.data.object;
    const paymentIntent = typeof charge.payment_intent === 'string'
      ? charge.payment_intent
      : charge.payment_intent?.id;

    if (paymentIntent) {
      const supabase = getAdminSupabase();
      const { error: refundError } = await supabase
        .from('purchases')
        .update({ status: 'refunded', analyses_remaining: 0 })
        .eq('stripe_payment_intent', paymentIntent);

      if (refundError) {
        console.error('Failed to mark purchase as refunded:', refundError);
      }
    }
  }

  return NextResponse.json({ received: true });
}
