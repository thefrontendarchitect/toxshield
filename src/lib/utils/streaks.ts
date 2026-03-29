import { startOfISOWeek, differenceInCalendarWeeks } from 'date-fns';
import { SupabaseClient } from '@supabase/supabase-js';

interface StreakUpdate {
  newStreak: number;
  newLongest: number;
  isNewWeek: boolean;
}

export function computeStreakUpdate(
  lastActivityDate: string | null,
  currentStreak: number,
  longestStreak: number
): StreakUpdate {
  const now = new Date();
  const currentWeekStart = startOfISOWeek(now);

  if (!lastActivityDate) {
    return { newStreak: 1, newLongest: Math.max(longestStreak, 1), isNewWeek: true };
  }

  const lastDate = new Date(lastActivityDate);
  const lastWeekStart = startOfISOWeek(lastDate);
  const weekDiff = differenceInCalendarWeeks(currentWeekStart, lastWeekStart, { weekStartsOn: 1 });

  if (weekDiff === 0) {
    // Same week — no streak change
    return { newStreak: currentStreak, newLongest: longestStreak, isNewWeek: false };
  } else if (weekDiff === 1) {
    // Consecutive week — increment
    const newStreak = currentStreak + 1;
    return { newStreak, newLongest: Math.max(longestStreak, newStreak), isNewWeek: true };
  } else {
    // Gap — reset
    return { newStreak: 1, newLongest: longestStreak, isNewWeek: true };
  }
}

/**
 * Update streak after a successful analysis. Fire-and-forget — errors are logged, not thrown.
 */
export async function updateStreakAfterAnalysis(
  supabase: SupabaseClient,
  userId: string
): Promise<void> {
  try {
    const { data: streak } = await supabase
      .from('streaks')
      .select('*')
      .eq('user_id', userId)
      .maybeSingle();

    const { newStreak, newLongest, isNewWeek } = computeStreakUpdate(
      streak?.last_activity_date ?? null,
      streak?.current_streak ?? 0,
      streak?.longest_streak ?? 0
    );

    if (isNewWeek || !streak) {
      await supabase.from('streaks').upsert({
        user_id: userId,
        current_streak: newStreak,
        longest_streak: newLongest,
        last_activity_date: new Date().toISOString().split('T')[0],
        streak_freezes: streak?.streak_freezes ?? 1,
      } as Record<string, unknown>, { onConflict: 'user_id' });
    }
  } catch (err) {
    console.error('[streaks] Failed to update streak:', err);
  }
}

/**
 * Check and award badges after analysis. Fire-and-forget.
 */
export async function checkAndAwardBadges(
  supabase: SupabaseClient,
  userId: string,
  totalAnalyses: number,
  totalPeople: number,
  currentStreak: number
): Promise<void> {
  try {
    // Fetch all badge definitions and user's existing badges in parallel
    const [{ data: allBadges }, { data: earnedBadges }] = await Promise.all([
      supabase.from('badge_definitions').select('*'),
      supabase.from('user_badges').select('badge_id').eq('user_id', userId),
    ]);

    if (!allBadges) return;

    const earnedIds = new Set((earnedBadges ?? []).map((b: { badge_id: string }) => b.badge_id));
    const newBadges: string[] = [];

    for (const badge of allBadges) {
      if (earnedIds.has(badge.id)) continue;
      if (!badge.threshold) continue;

      let qualifies = false;
      if (badge.id === 'first_analysis') qualifies = totalAnalyses >= 1;
      else if (badge.category === 'streak') qualifies = currentStreak >= badge.threshold;
      else if (badge.id.startsWith('analyses_')) qualifies = totalAnalyses >= badge.threshold;
      else if (badge.id.startsWith('people_')) qualifies = totalPeople >= badge.threshold;

      if (qualifies) newBadges.push(badge.id);
    }

    if (newBadges.length > 0) {
      await supabase.from('user_badges').insert(
        newBadges.map((badgeId) => ({
          user_id: userId,
          badge_id: badgeId,
        })) as Record<string, unknown>[]
      );
    }
  } catch (err) {
    console.error('[badges] Failed to check badges:', err);
  }
}
