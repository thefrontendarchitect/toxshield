import { createClient } from '@/lib/supabase/server';
import { redirect } from 'next/navigation';
import { ThreatProfile } from '@/components/analysis/threat-profile';
import { PersonHeader } from '@/components/people/person-header';
import { PersonRow, AnalysisRow } from '@/types/database';

interface PageProps { params: Promise<{ personId: string }>; }

export default async function PersonPage({ params }: PageProps) {
  const { personId } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect('/login');

  const { data: person } = await supabase.from('people').select('*').eq('id', personId).returns<PersonRow[]>().single();
  if (!person) redirect('/people');

  const { data: analysis, error: analysisError } = await supabase.from('analyses').select('*').eq('person_id', personId).order('created_at', { ascending: false }).limit(1).returns<AnalysisRow[]>().single();

  if (analysisError) {
    console.error('Analysis query failed for person', personId, analysisError);
  }

  return (
    <div>
      <PersonHeader personId={personId} personName={person.name} relationship={person.relationship} />
      {analysis ? (
        <ThreatProfile analysis={analysis} personName={person.name} relationship={person.relationship} />
      ) : (
        <div className="bg-surface border border-white/[0.06] rounded-xl p-10 text-center">
          <div className="text-3xl mb-3 font-mono text-white/15">[NO DATA]</div>
          <p className="text-white/40 font-mono text-sm mb-5">No analysis yet for this subject.</p>
          <a
            href={`/people/${personId}/add-info`}
            className="inline-block px-5 py-3 bg-white text-black font-bold rounded-xl font-mono text-sm min-h-[44px]"
          >
            Add Intel &amp; Analyze
          </a>
        </div>
      )}
    </div>
  );
}
