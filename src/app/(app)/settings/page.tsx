import { createClient } from '@/lib/supabase/server';
import { redirect } from 'next/navigation';
import { Profile } from '@/types/database';
import { ReferralCard } from '@/components/settings/referral-card';
import { SignOutButton } from './sign-out-button';
import Link from 'next/link';

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
            <label className="font-mono text-[10px] text-text-secondary uppercase tracking-wider">Name</label>
            <p className="font-mono text-sm text-text-primary">{profile?.display_name ?? 'Unknown Agent'}</p>
          </div>
          <div>
            <label className="font-mono text-[10px] text-text-secondary uppercase tracking-wider">Email</label>
            <p className="font-mono text-sm text-text-primary">{user.email}</p>
          </div>
          <div>
            <label className="font-mono text-[10px] text-text-secondary uppercase tracking-wider">Agent ID</label>
            <p className="font-mono text-[10px] text-text-secondary break-all">{user.id}</p>
          </div>
        </div>
      </div>

      {/* Referral */}
      <ReferralCard />

      {/* Quick links */}
      <div className="flex gap-3">
        <Link href="/my-insights" className="flex-1 card-dashed text-center py-3 font-mono text-[10px] text-neon-cyan/60 active:text-neon-cyan transition-colors touch-active">
          MY MIRROR
        </Link>
        <Link href="/wrapped" className="flex-1 card-dashed text-center py-3 font-mono text-[10px] text-neon-cyan/60 active:text-neon-cyan transition-colors touch-active">
          WRAPPED
        </Link>
        <Link href="/pricing" className="flex-1 card-dashed text-center py-3 font-mono text-[10px] text-neon-cyan/60 active:text-neon-cyan transition-colors touch-active">
          PRICING
        </Link>
      </div>

      <div className="card-dashed space-y-3">
        <h2 className="label-section">About ToxShield</h2>
        <p className="font-mono text-[10px] text-text-secondary leading-relaxed uppercase tracking-wider">
          ToxShield uses AI to analyze behavioral patterns. It helps you recognize toxic dynamics and protect yourself with actionable strategies.
        </p>
        <p className="font-mono text-[10px] text-text-secondary leading-relaxed uppercase tracking-wider">
          This tool is NOT a substitute for professional mental health support. If you are in immediate danger, please contact emergency services.
        </p>
      </div>

      <SignOutButton />
    </div>
  );
}
