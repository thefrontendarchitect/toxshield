import { createClient } from '@/lib/supabase/server';
import { getStripe } from '@/lib/stripe';
import { PACKS, type PackType } from '@/lib/packs';
import { NextResponse } from 'next/server';
import { z } from 'zod';

const requestSchema = z.object({
  pack: z.enum(['daily_boost', 'weekly_intel', 'monthly_pro']),
});

export async function POST(request: Request) {
  try {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body = await request.json();
    const parsed = requestSchema.safeParse(body);
    if (!parsed.success) {
      return NextResponse.json({ error: 'Invalid pack type' }, { status: 400 });
    }

    const packType = parsed.data.pack as PackType;
    const pack = PACKS[packType];

    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + pack.duration_days);

    // Clean up stale pending purchases (abandoned checkouts older than 1 hour)
    const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000).toISOString();
    const { error: cleanupError } = await supabase.from('purchases').update({ status: 'failed' } as Record<string, unknown>)
      .eq('user_id', user.id).eq('status', 'pending').lt('created_at', oneHourAgo);
    if (cleanupError) console.error('Failed to clean up stale purchases:', cleanupError);

    // Create Stripe Checkout Session (all packs are one-time payments)
    const description = packType === 'monthly_pro'
      ? 'Unlimited analyses for 30 days'
      : `${pack.analyses} analyses over ${pack.duration_days} day${pack.duration_days > 1 ? 's' : ''}`;

    const session = await getStripe().checkout.sessions.create({
      mode: 'payment',
      payment_method_types: ['card'],
      customer_email: user.email,
      line_items: [{
        price_data: {
          currency: 'usd',
          product_data: {
            name: `ToxShield ${pack.name}`,
            description,
          },
          unit_amount: pack.price_cents,
        },
        quantity: 1,
      }],
      metadata: {
        user_id: user.id,
        pack_type: packType,
      },
      success_url: `${process.env.NEXT_PUBLIC_APP_URL || request.headers.get('origin')}/checkout/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.NEXT_PUBLIC_APP_URL || request.headers.get('origin')}/pricing`,
    });

    // Store pending purchase
    const { error: insertError } = await supabase.from('purchases').insert({
      user_id: user.id,
      pack_type: packType,
      stripe_session_id: session.id,
      status: 'pending',
      analyses_granted: pack.analyses,
      analyses_remaining: pack.analyses,
      expires_at: expiresAt.toISOString(),
    } as Record<string, unknown>);

    if (insertError) {
      console.error('Failed to store pending purchase:', insertError);
      return NextResponse.json({ error: 'Failed to create checkout session' }, { status: 500 });
    }

    return NextResponse.json({ url: session.url });
  } catch (error) {
    console.error('Checkout error:', error);
    return NextResponse.json({ error: 'Failed to create checkout session' }, { status: 500 });
  }
}
