import { createClient } from '@/lib/supabase/server';
import { redirect } from 'next/navigation';
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
    <div className="space-y-6">
      {/* Hero Section */}
      <div className="space-y-3">
        <span className="tag-badge">SUBJECT REGISTRY</span>
        <h1 className="hero-title">PERSONNEL<br />MONITORING</h1>
        <p className="border-l-2 border-neon-cyan/20 pl-4 text-sm italic text-text-secondary leading-relaxed">
          &ldquo;Trust is a luxury the data suggests we cannot afford. Watch the fluctuations. Verify the anomalies.&rdquo;
        </p>
      </div>

      <PersonList people={allPeople} />
    </div>
  );
}
