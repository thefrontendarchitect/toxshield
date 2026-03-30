import { createClient } from '@/lib/supabase/server';
import { getRazorpay } from '@/lib/razorpay';
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

    // Create Razorpay order
    const razorpay = getRazorpay();
    const order = await razorpay.orders.create({
      amount: pack.price_paise,
      currency: 'INR',
      receipt: `txs_${packType}_${Date.now()}`,
      notes: {
        user_id: user.id,
        pack_type: packType,
      },
    });

    // Store pending purchase
    const { error: insertError } = await supabase.from('purchases').insert({
      user_id: user.id,
      pack_type: packType,
      payment_gateway: 'razorpay',
      razorpay_order_id: order.id,
      status: 'pending',
      analyses_granted: pack.analyses,
      analyses_remaining: pack.analyses,
      expires_at: expiresAt.toISOString(),
    } as Record<string, unknown>);

    if (insertError) {
      console.error('Failed to store pending purchase:', insertError);
      return NextResponse.json({ error: 'Failed to create order' }, { status: 500 });
    }

    return NextResponse.json({
      order_id: order.id,
      key_id: process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID,
      amount: pack.price_paise,
      currency: 'INR',
      name: 'ToxShield',
      description: `${pack.name} — ${pack.analyses === 9999 ? 'Unlimited' : pack.analyses} analyses`,
      prefill: {
        email: user.email,
      },
    });
  } catch (error) {
    console.error('Razorpay checkout error:', error);
    return NextResponse.json({ error: 'Failed to create order' }, { status: 500 });
  }
}
