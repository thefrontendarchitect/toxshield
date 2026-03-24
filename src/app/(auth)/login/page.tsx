'use client';

import { useState } from 'react';
import { createClient } from '@/lib/supabase/client';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { FormInput } from '@/components/ui/form-input';
import { ErrorAlert } from '@/components/ui/error-alert';
import { GoogleIcon } from '@/components/ui/google-icon';

const supabase = createClient();

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const { error } = await supabase.auth.signInWithPassword({ email, password });

    if (error) {
      setError(error.message);
      setLoading(false);
    } else {
      router.push('/dashboard');
    }
  };

  const handleGoogleLogin = async () => {
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: `${window.location.origin}/auth/callback` },
    });
  };

  return (
    <div className="w-full max-w-sm">
      <div className="bg-surface border border-white/[0.06] rounded-2xl overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b border-white/[0.06] text-center">
          <h1 className="text-2xl font-bold font-mono text-white text-glow tracking-[0.2em]">
            TOXSHIELD
          </h1>
          <p className="text-xs text-white/30 mt-1 font-mono tracking-wider">
            SYSTEM LOGIN REQUIRED
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleLogin} className="p-6 space-y-4">
          {error && <ErrorAlert message={error} />}

          <FormInput
            label="EMAIL"
            id="login-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="agent@toxshield.app"
            required
          />

          <FormInput
            label="PASSWORD"
            id="login-password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
          />

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-white text-black font-bold rounded-xl font-mono text-sm tracking-wider active:bg-white/90 transition-colors disabled:opacity-40 disabled:cursor-not-allowed min-h-[48px] touch-active"
          >
            {loading ? 'AUTHENTICATING...' : 'ACCESS SYSTEM →'}
          </button>

          <div className="relative my-4">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-white/[0.06]" />
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="bg-surface px-2 text-white/20 font-mono">OR</span>
            </div>
          </div>

          <button
            type="button"
            onClick={handleGoogleLogin}
            className="w-full py-3 border border-white/15 rounded-xl font-mono text-sm text-white active:bg-white/5 transition-colors flex items-center justify-center gap-2 min-h-[48px] touch-active"
          >
            <GoogleIcon />
            Continue with Google
          </button>
        </form>

        {/* Footer */}
        <div className="p-4 border-t border-white/[0.06] text-center">
          <p className="text-xs text-white/30 font-mono">
            No clearance?{' '}
            <Link href="/signup" className="text-white underline underline-offset-2">
              Request Access
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
