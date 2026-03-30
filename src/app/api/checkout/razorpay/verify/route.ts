import { createClient } from '@/lib/supabase/server';
import { PACKS, type PackType } from '@/lib/packs';
import { NextResponse } from 'next/server';
import { z } from 'zod';
import crypto from 'crypto';

const requestSchema = z.object({
  razorpay_order_id: z.string(),
  razorpay_payment_id: z.string(),
  razorpay_signature: z.string(),
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
      return NextResponse.json({ error: 'Invalid request' }, { status: 400 });
    }

    const { razorpay_order_id, razorpay_payment_id, razorpay_signature } = parsed.data;

    // HMAC SHA256 signature verification
    const secret = process.env.RAZORPAY_KEY_SECRET;
    if (!secret) {
      return NextResponse.json({ error: 'Server misconfiguration' }, { status: 500 });
    }

    const expectedSignature = crypto
      .createHmac('sha256', secret)
      .update(`${razorpay_order_id}|${razorpay_payment_id}`)
      .digest('hex');

    if (!crypto.timingSafeEqual(Buffer.from(razorpay_signature), Buffer.from(expectedSignature))) {
      return NextResponse.json({ error: 'Invalid payment signature' }, { status: 400 });
    }

    // Find and activate the purchase
    const { data: purchase } = await supabase
      .from('purchases')
      .select('id, pack_type, status')
      .eq('razorpay_order_id', razorpay_order_id)
      .eq('user_id', user.id)
      .returns<Array<{ id: string; pack_type: string; status: string }>>()
      .maybeSingle();

    if (!purchase) {
      return NextResponse.json({ error: 'Purchase not found' }, { status: 404 });
    }

    if (purchase.status === 'completed') {
      return NextResponse.json({ success: true, message: 'Already activated' });
    }

    // Set correct expiry from now (payment confirmed)
    const pack = PACKS[purchase.pack_type as PackType];
    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + pack.duration_days);

    const { error: updateError } = await supabase
      .from('purchases')
      .update({
        status: 'completed',
        razorpay_payment_id,
        expires_at: expiresAt.toISOString(),
      } as Record<string, unknown>)
      .eq('id', purchase.id);

    if (updateError) {
      console.error('Failed to activate purchase:', updateError);
      return NextResponse.json({ error: 'Failed to activate purchase' }, { status: 500 });
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Razorpay verify error:', error);
    return NextResponse.json({ error: 'Verification failed' }, { status: 500 });
  }
}
