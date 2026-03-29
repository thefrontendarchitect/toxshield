import { createClient } from '@/lib/supabase/server';
import { NextResponse } from 'next/server';

// Cache only the PUBLIC aggregate data — never cache per-user stats
let cachedPulse: { data: unknown; expiresAt: number } | null = null;
const CACHE_TTL = 5 * 60 * 1000;

export async function GET() {
  try {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    // Get cached public pulse or fetch fresh
    let pulseStats = cachedPulse && Date.now() < cachedPulse.expiresAt
      ? cachedPulse.data
      : null;

    if (!pulseStats) {
      const { data, error } = await supabase.rpc('get_pulse_stats');

      if (error) {
        console.error('Pulse RPC error:', error);
        pulseStats = {
          total_analyses: 0, total_users: 0, total_people: 0,
          avg_toxicity_score: 0, high_risk_percentage: 0,
          top_traits: [], analyses_this_week: 0,
          avg_score_this_week: 0, top_threat_types: [],
        };
      } else {
        pulseStats = data;
        cachedPulse = { data: pulseStats, expiresAt: Date.now() + CACHE_TTL };
      }
    }

    // Always compute per-user stats fresh (never cached)
    const [{ count: userAnalyses }, { data: userAvg }] = await Promise.all([
      supabase.from('analyses').select('*', { count: 'exact', head: true }).eq('user_id', user.id),
      supabase.from('analyses').select('toxicity_score').eq('user_id', user.id).returns<Array<{ toxicity_score: number }>>(),
    ]);

    const userAvgScore = userAvg && userAvg.length > 0
      ? Number((userAvg.reduce((sum, a) => sum + a.toxicity_score, 0) / userAvg.length).toFixed(1))
      : null;

    return NextResponse.json({
      pulse: pulseStats,
      user: { total_analyses: userAnalyses ?? 0, avg_toxicity_score: userAvgScore },
    });
  } catch (error) {
    console.error('Pulse error:', error);
    return NextResponse.json({ error: 'Failed to fetch pulse data' }, { status: 500 });
  }
}
