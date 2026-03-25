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
      className="w-full py-4 border border-dashed border-surface-3 rounded-lg font-mono text-xs uppercase tracking-[0.15em] text-white/40 active:bg-surface-2 transition-colors min-h-[48px] touch-active"
    >
      SIGN OUT
    </button>
  );
}
