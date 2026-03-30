import { createClient } from '@/lib/supabase/server';
import { redirect } from 'next/navigation';
import { calculateEnvironmentHealth } from '@/lib/ai/scoring';
import { StatsGrid } from '@/components/dashboard/stats-grid';
import { EnvironmentHealth } from '@/components/dashboard/environment-health';
import { StreakCounter } from '@/components/dashboard/streak-counter';
import { BadgeShelf } from '@/components/dashboard/badge-shelf';
import { HealthTrend } from '@/components/dashboard/health-trend';
import { NotificationPrompt } from '@/components/ui/notification-prompt';
import { ActivePack } from '@/components/dashboard/active-pack';
import { PolaroidCard } from '@/components/ui/polaroid-card';
import { PersonRow, StreakRow, BadgeDefinition, UserBadgeRow, HealthCheckinRow } from '@/types/database';
import { WarningIcon } from '@/components/ui/dossier-icons';
import Link from 'next/link';

function getInitials(name: string) {
  return name.split(/\s+/).map(w => w[0]).join('').toUpperCase().slice(0, 2);
}

function getStatusLabel(riskLevel: string | null) {
  if (riskLevel === 'high') return { label: 'CRITICAL', variant: 'critical' as const };
  if (riskLevel === 'moderate') return { label: 'MONITORED', variant: 'stable' as const };
  return { label: 'STABLE', variant: 'default' as const };
}

const rotations = [-2, 1.5, -1, 2.5, -1.5, 2];

export default async function DashboardPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect('/login');

  const { data: people } = await supabase
    .from('people').select('*').eq('user_id', user.id)
    .order('updated_at', { ascending: false }).returns<PersonRow[]>();

  const allPeople = people ?? [];
  const highRiskPeople = allPeople.filter((p) => p.current_risk_level === 'high');
  const highRiskCount = highRiskPeople.length;
  const { count: totalAnalyses } = await supabase
    .from('analyses').select('*', { count: 'exact', head: true }).eq('user_id', user.id);

  const health = calculateEnvironmentHealth(allPeople);

  // Fetch streak + badges + health checkins (parallel, non-blocking if tables don't exist yet)
  const today = new Date().toISOString().split('T')[0];
  const [{ data: streak }, { data: earnedBadges }, { data: allBadges }, { data: checkins }] = await Promise.all([
    supabase.from('streaks').select('*').eq('user_id', user.id).returns<StreakRow[]>().maybeSingle(),
    supabase.from('user_badges').select('badge_id, earned_at').eq('user_id', user.id).returns<Pick<UserBadgeRow, 'badge_id' | 'earned_at'>[]>(),
    supabase.from('badge_definitions').select('*').order('threshold').returns<BadgeDefinition[]>(),
    supabase.from('health_checkins').select('*').eq('user_id', user.id).order('checked_in_at', { ascending: false }).limit(30).returns<HealthCheckinRow[]>(),
  ]).catch(() => [{ data: null }, { data: null }, { data: null }, { data: null }]);

  const earnedIds = new Set((earnedBadges ?? []).map((b) => b.badge_id));
  const badges = (allBadges ?? []).map((badge) => ({
    ...badge,
    earned: earnedIds.has(badge.id),
  }));

  return (
    <div className="space-y-6">
      {/* Push notification prompt */}
      <NotificationPrompt />

      {/* Active pack status */}
      <ActivePack />

      {/* Stats + Health */}
      <div className="space-y-4">
        <StatsGrid totalPeople={allPeople.length} highRiskCount={highRiskCount} totalAnalyses={totalAnalyses ?? 0} />
        <EnvironmentHealth
          health={health}
          todayMood={(checkins ?? []).find((c) => c.checked_in_at === today)?.mood ?? null}
        />
        {(checkins ?? []).length >= 2 && (
          <HealthTrend checkins={(checkins ?? []).map((c) => ({ checked_in_at: c.checked_in_at, mood: c.mood }))} />
        )}
      </div>

      {/* Streak + Badges */}
      {streak && (
        <div className="space-y-3">
          <StreakCounter
            currentStreak={streak.current_streak ?? 0}
            longestStreak={streak.longest_streak ?? 0}
          />
          {badges.length > 0 && <BadgeShelf badges={badges} />}
        </div>
      )}

      {/* Wrapped CTA */}
      {(totalAnalyses ?? 0) > 0 && (
        <Link
          href="/wrapped"
          className="block card-dashed text-center py-4 font-mono text-xs text-neon-cyan/60 active:text-neon-cyan transition-colors touch-active"
        >
          VIEW YOUR WRAPPED REPORT &rarr;
        </Link>
      )}

      {/* High-Risk Threats */}
      {highRiskPeople.length > 0 && (
        <div>
          <p className="label-section mb-3">HIGH-RISK THREATS</p>
          <div className="arcane-glass overflow-hidden">
            {highRiskPeople.slice(0, 5).map((person, i) => (
              <Link
                key={person.id}
                href={`/people/${person.id}`}
                className={`flex items-center justify-between px-4 py-3 min-h-[56px] active:bg-neon-cyan/5 transition-colors ${
                  i < highRiskPeople.length - 1 ? 'border-b border-neon-cyan/[0.06]' : ''
                }`}
              >
                <div>
                  <p className="font-mono text-sm font-bold text-text-primary uppercase">
                    {person.name.toUpperCase().replace(/\s/g, '_')}
                  </p>
                  <p className="font-mono text-[10px] text-text-secondary uppercase">
                    {person.relationship ?? 'UNKNOWN'} &middot; SCORE: {person.current_toxicity_score?.toFixed(1) ?? '?'}
                  </p>
                </div>
                <WarningIcon size={20} className="text-neon-magenta shrink-0" aria-hidden="true" />
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Subject Feed */}
      <div>
        <div className="mb-3">
          <h2 className="hero-title text-3xl mb-1">SUBJECT FEED</h2>
          <p className="font-mono text-[10px] text-neon-cyan/30 uppercase tracking-[0.15em]">
            SURVEILLANCE DATA // SECURE_CHANNEL
          </p>
        </div>

        {allPeople.length === 0 ? (
          <div className="card-dashed text-center py-10">
            <p className="font-mono text-sm text-text-secondary mb-4">NO SUBJECTS IN REGISTRY</p>
            <Link
              href="/analyze"
              className="inline-block card-dashed px-6 py-3 font-mono text-xs uppercase tracking-[0.15em] text-neon-cyan/60 hover:text-neon-cyan transition-colors"
            >
              + INITIATE ANALYSIS
            </Link>
          </div>
        ) : (
          <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide -mx-4 px-4">
            {allPeople.slice(0, 8).map((person, i) => {
              const status = getStatusLabel(person.current_risk_level);
              return (
                <PolaroidCard
                  key={person.id}
                  name={person.name}
                  initials={getInitials(person.name)}
                  status={status.label}
                  statusVariant={status.variant}
                  rotation={rotations[i % rotations.length]}
                  href={`/people/${person.id}`}
                  relationship={person.relationship ?? undefined}
                  threatType={person.current_threat_type ?? undefined}
                />
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
