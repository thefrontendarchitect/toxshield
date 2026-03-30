import Link from 'next/link';
import type { Metadata } from 'next';
import { AuroraBackground } from '@/components/ui/aurora-background';

export const metadata: Metadata = {
  title: 'Delete Account | ToxShield',
  description:
    'Request deletion of your ToxShield account and all associated data.',
};

export default function DeleteAccountPage() {
  return (
    <div className="min-h-screen flex flex-col bg-surface-0/50 relative overflow-hidden">
      <AuroraBackground seed={555} />

      {/* Terminal header bar */}
      <div className="relative z-10 flex items-center gap-2 px-4 py-2 arcane-glass border-b border-neon-cyan/[0.08] font-mono text-xs pt-safe">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-neon-magenta/60" />
          <span className="w-2 h-2 rounded-full bg-warning-amber/60" />
          <span className="w-2 h-2 rounded-full bg-neon-mint/60" />
        </div>
        <div className="flex-1 text-center text-text-secondary">
          toxshield://delete-account
        </div>
      </div>

      <main className="relative z-10 flex-1 px-4 py-8">
        <div className="max-w-lg mx-auto space-y-6">
          {/* Back link */}
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 font-mono text-xs text-neon-cyan/60 active:text-neon-cyan transition-colors min-h-[44px]"
          >
            &larr; Back
          </Link>

          {/* Header */}
          <div className="arcane-glass-intense p-6 sm:p-8 space-y-2">
            <p className="font-mono text-[10px] text-neon-magenta tracking-[0.3em] uppercase">
              // account_deletion
            </p>
            <h1 className="text-2xl sm:text-3xl font-bold font-display text-text-primary tracking-[0.1em] text-glow">
              DELETE ACCOUNT
            </h1>
          </div>

          {/* Content */}
          <div className="arcane-glass-intense p-6 sm:p-8 space-y-6">
            <div className="space-y-3">
              <h2 className="font-mono text-sm font-bold text-neon-cyan uppercase tracking-[0.15em] text-glow-subtle">
                What Gets Deleted
              </h2>
              <p className="text-sm text-text-secondary leading-relaxed">
                When you request account deletion, we permanently remove <strong className="text-text-primary">all</strong> data
                associated with your account within 30 days:
              </p>
              <ul className="list-disc list-inside text-sm text-text-secondary leading-relaxed space-y-1.5">
                <li>Your profile (name, email, avatar)</li>
                <li>All people you&apos;ve added and their analysis history</li>
                <li>All AI-generated analysis results and inputs</li>
                <li>Mood check-in data</li>
                <li>Streaks, badges, and gamification data</li>
                <li>Purchase records</li>
                <li>Referral data</li>
                <li>Push notification subscriptions</li>
              </ul>
            </div>

            <div className="border-t border-neon-cyan/[0.08]" />

            <div className="space-y-3">
              <h2 className="font-mono text-sm font-bold text-neon-cyan uppercase tracking-[0.15em] text-glow-subtle">
                How to Delete Your Account
              </h2>
              <p className="text-sm text-text-secondary leading-relaxed">
                Send an email to the address below from the email address associated with your ToxShield
                account. Include &ldquo;Delete My Account&rdquo; in the subject line.
              </p>
              <div className="arcane-glass p-4 font-mono text-center">
                <Link
                  href="mailto:privacy@toxshield.in?subject=Delete%20My%20Account"
                  className="text-neon-cyan text-sm underline underline-offset-2 text-glow-subtle"
                >
                  privacy@toxshield.in
                </Link>
              </div>
              <p className="text-xs text-text-secondary/60 leading-relaxed">
                We will verify your identity and process the deletion within 30 days. You will receive
                a confirmation email once your data has been permanently deleted. This action is
                irreversible.
              </p>
            </div>

            <div className="border-t border-neon-cyan/[0.08]" />

            <div className="space-y-3">
              <h2 className="font-mono text-sm font-bold text-neon-cyan uppercase tracking-[0.15em] text-glow-subtle">
                Important Notes
              </h2>
              <ul className="list-disc list-inside text-sm text-text-secondary leading-relaxed space-y-1.5">
                <li>Active analysis packs will be forfeited upon deletion</li>
                <li>Anonymized, aggregated analytics data (containing no personal information) may be retained</li>
                <li>Purchase records may be retained for the minimum period required by applicable financial/tax laws</li>
              </ul>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-center gap-4 pb-safe">
            <Link
              href="/privacy"
              className="font-mono text-[10px] text-text-secondary/40 active:text-neon-cyan/60 transition-colors py-2 px-1"
            >
              Privacy Policy
            </Link>
            <span className="text-text-secondary/20">|</span>
            <Link
              href="/"
              className="font-mono text-[10px] text-text-secondary/40 active:text-neon-cyan/60 transition-colors py-2 px-1"
            >
              Home
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
