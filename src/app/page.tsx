import Link from 'next/link';
import { AuroraBackground } from '@/components/ui/aurora-background';
import { TapToAnalyze } from '@/components/analysis/tap-to-analyze';
import { HomepageTracker } from '@/components/analytics/homepage-tracker';

const jsonLd = [
  {
    '@context': 'https://schema.org',
    '@type': 'WebApplication',
    name: 'ToxShield',
    url: 'https://toxshield.in',
    description: 'AI-powered behavioral analysis. Log a person, get a threat profile.',
    applicationCategory: 'HealthApplication',
    operatingSystem: 'Web',
    offers: {
      '@type': 'Offer',
      price: '0',
      priceCurrency: 'USD',
    },
  },
  {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'ToxShield',
    url: 'https://toxshield.in',
    logo: 'https://toxshield.in/apple-icon.png',
    sameAs: [
      'https://www.instagram.com/toxshield.ai/',
      'https://www.youtube.com/@toxshield',
    ],
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col bg-surface-0/50 relative overflow-hidden">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <AuroraBackground seed={777} />
      <HomepageTracker />

      {/* Terminal header bar */}
      <div className="relative z-10 flex items-center gap-2 px-4 py-2 arcane-glass border-b border-neon-cyan/[0.08] font-mono text-xs pt-safe">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-neon-magenta/60" />
          <span className="w-2 h-2 rounded-full bg-warning-amber/60" />
          <span className="w-2 h-2 rounded-full bg-neon-mint/60" />
        </div>
        <div className="flex-1 text-center text-text-secondary">
          toxshield
        </div>
      </div>

      <main className="relative z-10 flex-1 px-5 py-8">
        <div className="max-w-lg w-full mx-auto space-y-8">

          {/* Hero — tight, no wasted space */}
          <div className="text-center space-y-3">
            <h1 className="text-4xl sm:text-6xl font-black font-display text-text-primary tracking-[0.15em] text-glow leading-[0.9]">
              TOX<span className="text-neon-cyan">SHIELD</span>
            </h1>
            <p className="text-sm text-text-secondary">
              Describe the behavior. <span className="text-neon-cyan font-medium">AI builds the threat profile.</span>
            </p>
          </div>

          {/* Tap-to-analyze — the main event, visible on first screen */}
          <div data-track="try_form">
            <TapToAnalyze />
          </div>

          {/* How it works — 3 steps */}
          <div data-track="how_it_works" className="space-y-3">
            <p className="font-mono text-[10px] text-neon-cyan/80 tracking-[0.25em] uppercase mb-4 text-center">
              // how_it_works
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-left">
              {[
                {
                  step: '01',
                  color: 'text-neon-cyan',
                  borderColor: 'hover:border-neon-cyan/30',
                  title: 'Describe',
                  desc: 'Log what they said, how they acted, or paste a chat.',
                },
                {
                  step: '02',
                  color: 'text-neon-magenta',
                  borderColor: 'hover:border-neon-magenta/30',
                  title: 'Analyze',
                  desc: 'AI scans for 40+ toxic traits — narcissism, gaslighting, DARVO, and more.',
                },
                {
                  step: '03',
                  color: 'text-neon-mint',
                  borderColor: 'hover:border-neon-mint/30',
                  title: 'Protect',
                  desc: 'Get a threat score, pattern breakdown, and protection strategies.',
                },
              ].map((feature) => (
                <div
                  key={feature.title}
                  className={`arcane-glass p-4 transition-all ${feature.borderColor}`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`font-mono text-xl font-black ${feature.color}`}>
                      {feature.step}
                    </span>
                    <h2 className="font-mono text-sm font-bold text-text-primary">
                      {feature.title}
                    </h2>
                  </div>
                  <p className="text-xs text-text-secondary leading-relaxed">{feature.desc}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Social proof */}
          <div className="flex items-center justify-center gap-6 py-2">
            <div className="text-center">
              <p className="font-mono text-2xl font-black text-text-primary text-glow-subtle">40+</p>
              <p className="font-mono text-[10px] text-text-secondary uppercase tracking-[0.1em]">Toxic Traits</p>
            </div>
            <div className="w-px h-8 bg-neon-cyan/10" />
            <div className="text-center">
              <p className="font-mono text-2xl font-black text-neon-cyan text-glow-subtle">AI</p>
              <p className="font-mono text-[10px] text-text-secondary uppercase tracking-[0.1em]">Powered</p>
            </div>
            <div className="w-px h-8 bg-neon-cyan/10" />
            <div className="text-center">
              <p className="font-mono text-2xl font-black text-text-primary text-glow-subtle">100%</p>
              <p className="font-mono text-[10px] text-text-secondary uppercase tracking-[0.1em]">Private</p>
            </div>
          </div>

          {/* CTA buttons */}
          <div data-track="cta" className="flex flex-col items-center gap-3 pt-2">
            <Link
              href="/try"
              data-track-click="full_analysis"
              className="w-full sm:w-auto px-12 py-4 bg-neon-cyan text-surface-0 font-black rounded-xl font-mono text-sm tracking-[0.15em] active:bg-neon-cyan/90 transition-all glow min-h-[52px] flex items-center justify-center touch-active uppercase"
            >
              Full Analysis — No Signup →
            </Link>
            <div className="flex gap-3">
              <Link
                href="/signup"
                data-track-click="signup"
                className="px-8 py-3.5 arcane-glass font-mono text-sm text-neon-cyan active:bg-neon-cyan/10 transition-colors min-h-[48px] flex items-center touch-active hover:border-neon-cyan/30"
              >
                SIGN UP
              </Link>
              <Link
                href="/login"
                data-track-click="login"
                className="px-8 py-3.5 arcane-glass font-mono text-sm text-text-secondary active:bg-neon-cyan/5 transition-colors min-h-[48px] flex items-center touch-active"
              >
                LOGIN
              </Link>
            </div>
          </div>

          <p className="text-[10px] text-text-secondary font-mono pt-4 text-center">
            ToxShield identifies behavioral patterns. Not a substitute for professional counseling.
          </p>

          <div className="flex items-center justify-center gap-4 pt-2 pb-safe">
            <Link href="/privacy" data-track-click="privacy_policy" data-track-type="link" className="font-mono text-[10px] text-text-secondary/40 active:text-neon-cyan/60 transition-colors py-2 px-1">
              Privacy Policy
            </Link>
            <span className="text-text-secondary/20">|</span>
            <Link href="/terms" data-track-click="terms_of_service" data-track-type="link" className="font-mono text-[10px] text-text-secondary/40 active:text-neon-cyan/60 transition-colors py-2 px-1">
              Terms of Service
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
