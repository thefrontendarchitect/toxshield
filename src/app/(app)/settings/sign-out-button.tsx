'use client';

import { createClient } from '@/lib/supabase/client';
import { useRouter } from 'next/navigation';

export function SignOutButton() {
  const router = useRouter();

  const handleSignOut = async () => {
    const supabase = createClient();
    await supabase.auth.signOut();
    router.push('/login');
  };

  return (
    <button
      onClick={handleSignOut}
      className="w-full py-4 bg-white/10 border border-white/15 rounded-xl font-mono text-sm text-white active:bg-white/20 transition-colors min-h-[48px] touch-active"
    >
      Sign Out
    </button>
  );
}
