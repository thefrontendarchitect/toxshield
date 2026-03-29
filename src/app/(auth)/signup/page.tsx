'use client';

import { useState } from 'react';
import { createClient } from '@/lib/supabase/client';
import Link from 'next/link';
import { FormInput } from '@/components/ui/form-input';
import { ErrorAlert } from '@/components/ui/error-alert';
import { GoogleIcon } from '@/components/ui/google-icon';

const supabase = createClient();

export default function SignupPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: { full_name: name },
        emailRedirectTo: `${window.location.origin}/auth/callback`,
      },
    });

    if (error) {
      setError(error.message);
    } else {
      setSuccess(true);
    }
    setLoading(false);
  };

  const handleGoogleSignup = async () => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: `${window.location.origin}/auth/callback` },
    });
    if (error) setError(error.message);
  };

  if (success) {
    return (
      <div className="w-full max-w-sm">
        <div className="arcane-glass-intense p-6 text-center">
          <div className="text-4xl mb-4">
            <span className="text-neon-cyan text-glow font-mono font-bold">[OK]</span>
          </div>
          <h2 className="text-lg font-mono text-text-primary mb-2">ACCESS REQUEST SUBMITTED</h2>
          <p className="text-sm text-text-secondary font-mono">
            Check your email to confirm your identity and activate your ToxShield clearance.
          </p>
          <Link
            href="/login"
            className="inline-block mt-4 px-4 py-2.5 border border-neon-cyan/20 rounded-xl font-mono text-sm text-neon-cyan active:bg-neon-cyan/5 transition-colors"
          >
            Return to Login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-sm">
      <div className="arcane-glass-intense overflow-hidden">
        <div className="p-6 border-b border-neon-cyan/[0.08] text-center">
          <h1 className="text-2xl font-bold font-mono text-text-primary text-glow tracking-[0.2em]">
            TOXSHIELD
          </h1>
          <p className="text-xs text-neon-cyan/30 mt-1 font-mono tracking-wider">
            NEW AGENT REGISTRATION
          </p>
        </div>

        <form onSubmit={handleSignup} className="p-6 space-y-4">
          {error && <ErrorAlert message={error} />}

          <FormInput
            label="AGENT NAME"
            id="signup-name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Agent Smith"
            required
          />

          <FormInput
            label="EMAIL"
            id="signup-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="agent@toxshield.app"
            required
          />

          <div>
            <FormInput
              label="PASSWORD"
              id="signup-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              minLength={6}
            />
            <p className="text-xs text-text-secondary/50 font-mono mt-1">Minimum 6 characters</p>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-neon-cyan text-surface-0 font-bold rounded-xl font-mono text-sm tracking-wider active:bg-neon-cyan/90 transition-colors disabled:opacity-40 disabled:cursor-not-allowed min-h-[48px] touch-active glow-subtle"
          >
            {loading ? 'PROCESSING...' : 'INITIALIZE CLEARANCE →'}
          </button>

          <div className="relative my-4">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-neon-cyan/[0.08]" />
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="bg-surface-1 px-2 text-neon-cyan/20 font-mono">OR</span>
            </div>
          </div>

          <button
            type="button"
            onClick={handleGoogleSignup}
            className="w-full py-3 border border-neon-cyan/15 rounded-xl font-mono text-sm text-text-primary active:bg-neon-cyan/5 transition-colors flex items-center justify-center gap-2 min-h-[48px] touch-active"
          >
            <GoogleIcon />
            Continue with Google
          </button>
        </form>

        <div className="p-4 border-t border-neon-cyan/[0.08] text-center space-y-2">
          <p className="text-xs text-text-secondary font-mono">
            Already have clearance?{' '}
            <Link href="/login" className="text-neon-cyan underline underline-offset-2">Login</Link>
          </p>
          <p className="text-xs text-text-secondary/60 font-mono">
            or{' '}
            <Link href="/try" className="text-neon-cyan/50 underline underline-offset-2">
              Try without signing up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
