import { createClient } from '@/lib/supabase/server';
import { NextResponse } from 'next/server';
import { StreakRow, UserBadgeRow, BadgeDefinition } from '@/types/database';

export async function GET() {
  try {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Fetch streak, earned badges, and all badge definitions in parallel
    const [{ data: streak }, { data: earnedBadges }, { data: allBadges }] = await Promise.all([
      supabase.from('streaks').select('*').eq('user_id', user.id).returns<StreakRow[]>().maybeSingle(),
      supabase.from('user_badges').select('badge_id, earned_at').eq('user_id', user.id).returns<Pick<UserBadgeRow, 'badge_id' | 'earned_at'>[]>(),
      supabase.from('badge_definitions').select('*').order('threshold').returns<BadgeDefinition[]>(),
    ]);

    const earnedIds = new Set((earnedBadges ?? []).map((b) => b.badge_id));

    const badges = (allBadges ?? []).map((badge) => ({
      ...badge,
      earned: earnedIds.has(badge.id),
      earned_at: (earnedBadges ?? []).find((b) => b.badge_id === badge.id)?.earned_at ?? null,
    }));

    return NextResponse.json({
      streak: streak ?? { current_streak: 0, longest_streak: 0, last_activity_date: null, streak_freezes: 1 },
      badges,
    });
  } catch (error) {
    console.error('Streaks error:', error);
    return NextResponse.json({ error: 'Failed to fetch streaks' }, { status: 500 });
  }
}
