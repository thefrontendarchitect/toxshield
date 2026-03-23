import { createClient } from '@/lib/supabase/server';
import { redirect } from 'next/navigation';
import Link from 'next/link';
import { PersonRow } from '@/types/database';
import { PersonList } from '@/components/people/person-list';

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

      <PersonList people={allPeople} />
    </div>
  );
}
