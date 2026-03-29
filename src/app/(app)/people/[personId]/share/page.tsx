import { createClient } from '@/lib/supabase/server';
import { redirect } from 'next/navigation';
import { PersonRow, AnalysisRow } from '@/types/database';
import { ShareCard } from '@/components/people/share-card';

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

  return (
    <div>
      <div className="mb-6">
        <p className="text-xs text-text-secondary font-mono">Preview and share this threat profile</p>
      </div>

      <ShareCard analysis={analysis} personName={person.name} />
    </div>
  );
}
