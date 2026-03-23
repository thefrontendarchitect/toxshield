import { createClient } from '@/lib/supabase/server';
import { redirect } from 'next/navigation';
import { ThreatProfile } from '@/components/analysis/threat-profile';
import { PersonRow, AnalysisRow } from '@/types/database';
import Link from 'next/link';

interface PageProps { params: Promise<{ personId: string }>; }

export default async function PersonPage({ params }: PageProps) {
  const { personId } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect('/login');

  const { data: person } = await supabase.from('people').select('*').eq('id', personId).returns<PersonRow[]>().single();
  if (!person) redirect('/people');

  const { data: analysis } = await supabase.from('analyses').select('*').eq('person_id', personId).order('created_at', { ascending: false }).limit(1).returns<AnalysisRow[]>().single();
  if (!analysis) redirect('/people');

  return (
    <div>
      <div className="flex items-center gap-2 mb-5">
        <Link
          href={`/people/${personId}/add-info`}
          className="flex-1 py-3 border border-white/15 rounded-xl font-mono text-xs text-white active:bg-white/5 transition-colors text-center min-h-[44px] flex items-center justify-center touch-active"
        >
          + Add Intel
        </Link>
        <Link
          href={`/people/${personId}/share`}
          className="flex-1 py-3 bg-white text-black font-bold rounded-xl font-mono text-xs active:bg-white/90 transition-colors text-center min-h-[44px] flex items-center justify-center touch-active"
        >
          Share Report
        </Link>
      </div>
      <ThreatProfile analysis={analysis} personName={person.name} relationship={person.relationship} />
    </div>
  );
}
