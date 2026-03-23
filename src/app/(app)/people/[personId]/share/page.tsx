import { createClient } from '@/lib/supabase/server';
import { redirect } from 'next/navigation';
import { ToxicTrait, RiskLevel } from '@/types/analysis';
import { PersonRow, AnalysisRow } from '@/types/database';

interface PageProps { params: Promise<{ personId: string }>; }

export default async function SharePage({ params }: PageProps) {
  const { personId } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect('/login');

  const { data: person } = await supabase.from('people').select('*').eq('id', personId).returns<PersonRow[]>().single();
  if (!person) redirect('/people');

  const { data: analysis } = await supabase.from('analyses').select('*').eq('person_id', personId).order('created_at', { ascending: false }).limit(1).returns<AnalysisRow[]>().single();
  if (!analysis) redirect('/people');

  const traits = analysis.detected_traits as unknown as ToxicTrait[];
  const riskLevel = analysis.risk_level as RiskLevel;
  const isHigh = riskLevel === 'high';

  return (
    <div>
      <div className="mb-6">
        <p className="text-xs text-white/30 font-mono">Preview and share this threat profile</p>
      </div>

      {/* Share card preview */}
      <div className="bg-black border-2 border-white/15 rounded-2xl p-6 space-y-5">
        <div className="text-center space-y-2">
          <p className="text-[10px] text-white/30 font-mono tracking-[0.3em] uppercase">ToxShield Analysis</p>
          <h2 className="text-lg font-bold font-mono text-white">&ldquo;{analysis.headline}&rdquo;</h2>
          <p className="text-xs text-white/40 italic">{analysis.tagline}</p>
        </div>

        <div className="flex justify-center">
          <div className={`w-20 h-20 rounded-full flex items-center justify-center font-mono text-2xl font-bold border-2 border-white text-white ${isHigh ? 'glow' : riskLevel === 'moderate' ? 'opacity-70' : 'opacity-40'}`}>
            {analysis.toxicity_score.toFixed(1)}
          </div>
        </div>

        <div className="flex flex-wrap justify-center gap-2">
          {traits.slice(0, 3).map((trait) => (
            <span key={trait.name} className="px-3 py-1.5 bg-white/8 border border-white/15 rounded-full font-mono text-xs text-white/70">
              {trait.name}
            </span>
          ))}
        </div>

        <p className="text-center text-[10px] text-white/20 font-mono">Analyze your circle → toxshield.app</p>
      </div>

      <div className="mt-5 grid grid-cols-2 gap-3">
        <button className="px-4 py-3.5 border border-white/15 rounded-xl font-mono text-xs text-white active:bg-white/5 transition-colors text-center min-h-[48px] touch-active">
          Copy Link
        </button>
        <button className="px-4 py-3.5 bg-white text-black font-bold rounded-xl font-mono text-xs active:bg-white/90 transition-colors text-center min-h-[48px] touch-active">
          Download Image
        </button>
      </div>
    </div>
  );
}
