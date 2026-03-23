import { createClient } from '@/lib/supabase/server';
import { redirect } from 'next/navigation';
import Link from 'next/link';
import { RISK_STYLES } from '@/lib/constants';
import { RiskLevel } from '@/types/analysis';
import { PersonRow } from '@/types/database';

export default async function PeoplePage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect('/login');

  const { data: people } = await supabase
    .from('people').select('*').eq('user_id', user.id)
    .order('current_toxicity_score', { ascending: false }).returns<PersonRow[]>();

  const allPeople = people ?? [];

  return (
    <div>
      <div className="flex items-center justify-between mb-5">
        <p className="text-xs text-white/30 font-mono">
          {allPeople.length} subject{allPeople.length !== 1 ? 's' : ''} logged
        </p>
        <Link
          href="/analyze"
          className="px-3 py-2 bg-white text-black font-bold rounded-lg font-mono text-xs active:bg-white/90 transition-colors min-h-[36px] flex items-center touch-active"
        >
          + New
        </Link>
      </div>

      {allPeople.length === 0 ? (
        <div className="bg-surface border border-white/[0.06] rounded-xl p-10 text-center">
          <div className="text-3xl mb-3 font-mono text-white/15">[EMPTY]</div>
          <p className="text-white/40 font-mono text-sm mb-5">No subjects in your database yet.</p>
          <Link
            href="/analyze"
            className="inline-block px-5 py-3 bg-white text-black font-bold rounded-xl font-mono text-sm min-h-[44px]"
          >
            Run Your First Analysis
          </Link>
        </div>
      ) : (
        <div className="space-y-2">
          {allPeople.map((person) => {
            const riskLevel = (person.current_risk_level ?? 'low') as RiskLevel;
            const riskStyle = RISK_STYLES[riskLevel];
            const isHigh = riskLevel === 'high';

            return (
              <Link
                key={person.id}
                href={`/people/${person.id}`}
                className="flex items-center justify-between p-4 bg-surface border border-white/[0.06] rounded-xl active:bg-hover transition-all touch-active min-h-[64px]"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-11 h-11 rounded-full flex items-center justify-center font-mono text-sm font-bold border border-white/20 text-white shrink-0 ${riskStyle} ${isHigh ? 'glow-subtle' : ''}`}>
                    {person.current_toxicity_score?.toFixed(1) ?? '—'}
                  </div>
                  <div className="min-w-0">
                    <p className="font-mono text-sm font-bold text-white truncate">{person.name}</p>
                    <div className="flex items-center gap-1.5 mt-0.5 flex-wrap">
                      <span className="text-xs text-white/30">{person.relationship ?? 'Unknown'}</span>
                      <span className="text-white/15 text-xs">·</span>
                      <span className={`text-xs font-mono uppercase text-white ${riskStyle}`}>{riskLevel}</span>
                      <span className="text-white/15 text-xs">·</span>
                      <span className="text-xs text-white/30">{person.analysis_count} report{person.analysis_count !== 1 ? 's' : ''}</span>
                    </div>
                  </div>
                </div>
                <span className="text-white/15 font-mono shrink-0 ml-2">→</span>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
