import { createClient } from '@/lib/supabase/server';
import { redirect } from 'next/navigation';
import { Profile } from '@/types/database';
import { SignOutButton } from './sign-out-button';

export default async function SettingsPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect('/login');

  const { data: profile } = await supabase.from('profiles').select('*').eq('id', user.id).returns<Profile[]>().single();

  return (
    <div className="space-y-4">
      <div className="card-dashed space-y-4">
        <h2 className="label-section">Agent Profile</h2>
        <div className="space-y-3">
          <div>
            <label className="font-mono text-[10px] text-white/20 uppercase tracking-wider">Name</label>
            <p className="font-mono text-sm text-white">{profile?.display_name ?? 'Unknown Agent'}</p>
          </div>
          <div>
            <label className="font-mono text-[10px] text-white/20 uppercase tracking-wider">Email</label>
            <p className="font-mono text-sm text-white">{user.email}</p>
          </div>
          <div>
            <label className="font-mono text-[10px] text-white/20 uppercase tracking-wider">Agent ID</label>
            <p className="font-mono text-[10px] text-white/30 break-all">{user.id}</p>
          </div>
        </div>
      </div>

      <div className="card-dashed space-y-3">
        <h2 className="label-section">About ToxShield</h2>
        <p className="font-mono text-[10px] text-white/30 leading-relaxed uppercase tracking-wider">
          ToxShield uses AI to analyze behavioral patterns. It helps you recognize toxic dynamics and protect yourself with actionable strategies.
        </p>
        <p className="font-mono text-[10px] text-white/30 leading-relaxed uppercase tracking-wider">
          This tool is NOT a substitute for professional mental health support. If you are in immediate danger, please contact emergency services.
        </p>
      </div>

      <SignOutButton />
    </div>
  );
}
