import Link from 'next/link';
import { AuroraBackground } from '@/components/ui/aurora-background';
import { QuickModeForm } from '@/components/analysis/quick-mode-form';

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
      'https://www.instagram.com/toxshield.in/',
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

      <main className="relative z-10 flex-1 flex items-center justify-center px-5 py-10">
        <div className="max-w-lg w-full text-center space-y-10">

          {/* Hero — big dramatic title */}
          <div className="space-y-5">
            <p className="font-mono text-[10px] text-neon-magenta tracking-[0.3em] uppercase">
              // threat_detection_system
            </p>
            <h1 className="text-5xl sm:text-7xl font-black font-display text-text-primary tracking-[0.15em] text-glow leading-[0.9]">
              TOX<span className="text-neon-cyan">SHIELD</span>
            </h1>
            <div className="flex items-center justify-center gap-3">
              <div className="h-[1px] w-12 bg-gradient-to-r from-transparent to-neon-cyan/40" />
              <p className="text-xs text-neon-cyan font-mono tracking-[0.2em] uppercase">
                Forensic Behavioral Analysis
              </p>
              <div className="h-[1px] w-12 bg-gradient-to-l from-transparent to-neon-cyan/40" />
            </div>
          </div>

          {/* Punchy value prop */}
          <div className="arcane-glass-intense p-6 space-y-4 max-w-md mx-auto text-left">
            <p className="text-text-primary text-base leading-relaxed">
              Someone in your life feels <span className="text-neon-magenta font-bold">off</span>.
              You can&apos;t quite name it. The subtle put-downs, the gaslighting,
              the way they twist every argument.
            </p>
            <p className="text-text-primary text-base leading-relaxed">
              <span className="text-neon-cyan font-bold">ToxShield sees it.</span> Describe the behavior.
              Our AI builds a forensic threat profile — toxicity score, detected
              manipulation traits, and strategies to protect yourself.
            </p>
            <div className="pt-2 border-t border-neon-cyan/[0.06]">
              <p className="text-neon-mint font-mono text-xs italic text-glow-subtle">
                &ldquo;Know who&apos;s toxic before they know you know.&rdquo;
              </p>
            </div>
          </div>

          {/* How it works — 3 steps */}
          <div className="space-y-3">
            <p className="font-mono text-[10px] text-neon-cyan/80 tracking-[0.25em] uppercase mb-4">
              // how_it_works
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-left">
              {[
                {
                  step: '01',
                  color: 'text-neon-cyan',
                  borderColor: 'hover:border-neon-cyan/30',
                  title: 'Describe',
                  desc: 'Log what they said, how they acted, or paste a chat. The more detail, the sharper the profile.',
                },
                {
                  step: '02',
                  color: 'text-neon-magenta',
                  borderColor: 'hover:border-neon-magenta/30',
                  title: 'Analyze',
                  desc: 'AI scans for 40+ toxic traits — narcissism, gaslighting, DARVO, love-bombing, and more.',
                },
                {
                  step: '03',
                  color: 'text-neon-mint',
                  borderColor: 'hover:border-neon-mint/30',
                  title: 'Protect',
                  desc: 'Get a threat score (0-10), pattern breakdown, and actionable protection strategies.',
                },
              ].map((feature) => (
                <div
                  key={feature.title}
                  className={`arcane-glass p-5 transition-all ${feature.borderColor}`}
                >
                  <div className="flex items-center gap-2 mb-3">
                    <span className={`font-mono text-2xl font-black ${feature.color}`}>
                      {feature.step}
                    </span>
                  </div>
                  <h2 className="font-mono text-sm font-bold text-text-primary mb-1.5">
                    {feature.title}
                  </h2>
                  <p className="text-xs text-text-secondary leading-relaxed">{feature.desc}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Social proof / stats */}
          <div className="flex items-center justify-center gap-6 py-2">
            <div className="text-center">
              <p className="font-mono text-2xl font-black text-text-primary text-glow-subtle">40+</p>
              <p className="font-mono text-[9px] text-text-secondary uppercase tracking-wider">Toxic Traits</p>
            </div>
            <div className="w-px h-8 bg-neon-cyan/10" />
            <div className="text-center">
              <p className="font-mono text-2xl font-black text-neon-cyan text-glow-subtle">AI</p>
              <p className="font-mono text-[9px] text-text-secondary uppercase tracking-wider">Powered</p>
            </div>
            <div className="w-px h-8 bg-neon-cyan/10" />
            <div className="text-center">
              <p className="font-mono text-2xl font-black text-text-primary text-glow-subtle">100%</p>
              <p className="font-mono text-[9px] text-text-secondary uppercase tracking-wider">Private</p>
            </div>
          </div>

          {/* Inline quick assess — zero clicks to value */}
          <div className="space-y-3 text-left">
            <p className="font-mono text-[10px] text-neon-cyan/80 tracking-[0.25em] uppercase text-center">
              // try_it_now — no signup required
            </p>
            <div className="arcane-glass-intense p-5">
              <QuickModeForm />
            </div>
          </div>

          {/* CTA buttons */}
          <div className="flex flex-col items-center gap-3 pt-2">
            <Link
              href="/try"
              className="w-full sm:w-auto px-12 py-4 bg-neon-cyan text-surface-0 font-black rounded-xl font-mono text-sm tracking-[0.15em] active:bg-neon-cyan/90 transition-all glow min-h-[52px] flex items-center justify-center touch-active uppercase"
            >
              Full Analysis — No Signup →
            </Link>
            <div className="flex gap-3">
              <Link
                href="/signup"
                className="px-8 py-3.5 arcane-glass font-mono text-sm text-neon-cyan active:bg-neon-cyan/10 transition-colors min-h-[48px] flex items-center touch-active hover:border-neon-cyan/30"
              >
                SIGN UP
              </Link>
              <Link
                href="/login"
                className="px-8 py-3.5 arcane-glass font-mono text-sm text-text-secondary active:bg-neon-cyan/5 transition-colors min-h-[48px] flex items-center touch-active"
              >
                LOGIN
              </Link>
            </div>
          </div>

          <p className="text-[10px] text-text-secondary font-mono pt-4">
            ToxShield identifies behavioral patterns. Not a substitute for professional counseling.
          </p>

          <div className="flex items-center justify-center gap-4 pt-2 pb-safe">
            <Link href="/privacy" className="font-mono text-[10px] text-text-secondary/40 active:text-neon-cyan/60 transition-colors py-2 px-1">
              Privacy Policy
            </Link>
            <span className="text-text-secondary/20">|</span>
            <Link href="/terms" className="font-mono text-[10px] text-text-secondary/40 active:text-neon-cyan/60 transition-colors py-2 px-1">
              Terms of Service
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
