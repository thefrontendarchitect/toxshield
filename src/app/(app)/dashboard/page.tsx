import { createClient } from '@/lib/supabase/server';
import { redirect } from 'next/navigation';
import { calculateEnvironmentHealth } from '@/lib/ai/scoring';
import { StatsGrid } from '@/components/dashboard/stats-grid';
import { EnvironmentHealth } from '@/components/dashboard/environment-health';
import { PersonRow } from '@/types/database';
import Link from 'next/link';

export default async function DashboardPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect('/login');

  const { data: people } = await supabase
    .from('people').select('*').eq('user_id', user.id)
    .order('updated_at', { ascending: false }).returns<PersonRow[]>();

  const allPeople = people ?? [];
  const highRiskCount = allPeople.filter((p) => p.current_risk_level === 'high').length;
  const { count: totalAnalyses } = await supabase
    .from('analyses').select('*', { count: 'exact', head: true }).eq('user_id', user.id);

  const health = calculateEnvironmentHealth(allPeople);

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <StatsGrid totalPeople={allPeople.length} highRiskCount={highRiskCount} totalAnalyses={totalAnalyses ?? 0} />
        <EnvironmentHealth health={health} />
      </div>

      {/* Primary CTA — inverted white */}
      <Link
        href="/analyze"
        className="flex items-center justify-center gap-2 w-full py-4 bg-white text-black font-bold rounded-xl font-mono text-sm tracking-wider active:bg-white/90 transition-all touch-active min-h-[48px]"
      >
        + New Analysis
      </Link>

      {/* Recent People */}
      <div>
        <h2 className="text-xs text-white/30 font-mono uppercase tracking-[0.15em] mb-3">
          Recent Subjects
        </h2>
        {allPeople.length === 0 ? (
          <div className="bg-surface border border-white/[0.06] rounded-xl p-8 text-center">
            <p className="text-white/40 font-mono text-sm mb-4">No subjects logged yet.</p>
            <Link
              href="/analyze"
              className="inline-block px-4 py-3 bg-white text-black font-bold rounded-xl font-mono text-sm min-h-[44px]"
            >
              + Analyze Someone
            </Link>
          </div>
        ) : (
          <div className="space-y-2">
            {allPeople.slice(0, 10).map((person) => {
              const isHigh = person.current_risk_level === 'high';
              const isModerate = person.current_risk_level === 'moderate';
              const scoreOpacity = isHigh ? 'opacity-100' : isModerate ? 'opacity-70' : 'opacity-40';

              return (
                <Link
                  key={person.id}
                  href={`/people/${person.id}`}
                  className="flex items-center justify-between p-4 bg-surface border border-white/[0.06] rounded-xl active:bg-hover transition-colors touch-active min-h-[64px]"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center font-mono text-sm font-bold border border-white/20 text-white ${scoreOpacity} ${isHigh ? 'glow-subtle' : ''}`}>
                      {person.current_toxicity_score?.toFixed(1) ?? '?'}
                    </div>
                    <div>
                      <p className="font-mono text-sm text-white">{person.name}</p>
                      <p className="text-xs text-white/30">
                        {person.relationship ?? 'Unknown'} · {person.analysis_count} analysis{person.analysis_count !== 1 ? 'es' : ''}
                      </p>
                    </div>
                  </div>
                  <span className="text-white/20 font-mono text-sm">→</span>
                </Link>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
