import { createClient } from '@/lib/supabase/server';
import { generateReferralCode } from '@/lib/utils/referrals';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    // Get or create referral code
    const { data: profile } = await supabase
      .from('profiles')
      .select('referral_code')
      .eq('id', user.id)
      .single();

    let referralCode = (profile as { referral_code: string | null } | null)?.referral_code;

    if (!referralCode) {
      referralCode = generateReferralCode();
      await supabase
        .from('profiles')
        .update({ referral_code: referralCode } as Record<string, unknown>)
        .eq('id', user.id);
    }

    // Get referral stats
    const { data: referrals } = await supabase
      .from('referrals')
      .select('id, status, created_at, completed_at')
      .eq('referrer_id', user.id)
      .order('created_at', { ascending: false });

    const completed = (referrals ?? []).filter((r: { status: string }) => r.status === 'completed').length;
    const pending = (referrals ?? []).filter((r: { status: string }) => r.status === 'pending').length;

    return NextResponse.json({
      referral_code: referralCode,
      referral_url: `https://toxshield.in/signup?ref=${referralCode}`,
      stats: {
        total: (referrals ?? []).length,
        completed,
        pending,
        bonus_earned: completed * 2,
      },
    });
  } catch (error) {
    console.error('Referrals error:', error);
    return NextResponse.json({ error: 'Failed to fetch referrals' }, { status: 500 });
  }
}
