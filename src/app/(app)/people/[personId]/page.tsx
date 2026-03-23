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

  const { data: analysis } = await supabase.from('analyses').select('*').eq('person_id', personId).order('created_at', { ascending: false }).limit(1).returns<AnalysisRow[]>().single();
  if (!analysis) redirect('/people');

  return (
    <div>
      <PersonHeader personId={personId} relationship={person.relationship} />
      <ThreatProfile analysis={analysis} personName={person.name} relationship={person.relationship} />
    </div>
  );
}
