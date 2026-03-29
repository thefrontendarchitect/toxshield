import { createClient } from '@/lib/supabase/server';
import { getMonthStart } from '@/lib/utils/usage';
import { NextResponse } from 'next/server';
import { z } from 'zod';

const redeemSchema = z.object({
  referral_code: z.string().min(1),
});

export async function POST(request: Request) {
  try {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    const body = await request.json();
    const parsed = redeemSchema.safeParse(body);
    if (!parsed.success) {
      return NextResponse.json({ error: 'Invalid referral code' }, { status: 400 });
    }

    const { referral_code } = parsed.data;

    // Find the referrer by code
    const { data: referrerProfile } = await supabase
      .from('profiles')
      .select('id')
      .eq('referral_code', referral_code)
      .single();

    if (!referrerProfile) {
      return NextResponse.json({ error: 'Invalid referral code' }, { status: 404 });
    }

    const referrerId = (referrerProfile as { id: string }).id;

    // Can't refer yourself
    if (referrerId === user.id) {
      return NextResponse.json({ error: 'Cannot use your own referral code' }, { status: 400 });
    }

    // Check if this user has already used ANY referral code (one per account)
    const { data: alreadyReferred } = await supabase
      .from('referrals')
      .select('id')
      .eq('referred_id', user.id)
      .eq('status', 'completed')
      .maybeSingle();

    if (alreadyReferred) {
      return NextResponse.json({ error: 'Already used a referral code' }, { status: 409 });
    }

    // Create referral record
    await supabase.from('referrals').insert({
      referrer_id: referrerId,
      referred_id: user.id,
      referral_code,
      status: 'completed',
      bonus_granted: true,
      completed_at: new Date().toISOString(),
    } as Record<string, unknown>);

    // Grant bonus analyses
    const monthStart = getMonthStart();

    // +2 for referrer
    const { data: referrerUsage } = await supabase
      .from('usage_tracking')
      .select('*')
      .eq('user_id', referrerId)
      .eq('period_start', monthStart)
      .maybeSingle();

    await supabase.from('usage_tracking').upsert({
      user_id: referrerId,
      period_start: monthStart,
      analyses_used: referrerUsage?.analyses_used ?? 0,
      bonus_analyses: (referrerUsage?.bonus_analyses ?? 0) + 2,
    } as Record<string, unknown>, { onConflict: 'user_id,period_start' });

    // +1 for referee
    const { data: refereeUsage } = await supabase
      .from('usage_tracking')
      .select('*')
      .eq('user_id', user.id)
      .eq('period_start', monthStart)
      .maybeSingle();

    await supabase.from('usage_tracking').upsert({
      user_id: user.id,
      period_start: monthStart,
      analyses_used: refereeUsage?.analyses_used ?? 0,
      bonus_analyses: (refereeUsage?.bonus_analyses ?? 0) + 1,
    } as Record<string, unknown>, { onConflict: 'user_id,period_start' });

    return NextResponse.json({ ok: true, bonus_referrer: 2, bonus_referee: 1 });
  } catch (error) {
    console.error('Referral redeem error:', error);
    return NextResponse.json({ error: 'Redemption failed' }, { status: 500 });
  }
}
