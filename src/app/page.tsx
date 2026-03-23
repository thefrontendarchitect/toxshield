import Link from 'next/link';

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col bg-black">
      {/* Minimal header */}
      <div className="flex items-center gap-2 px-4 py-2 bg-surface border-b border-white/[0.06] font-mono text-xs">
        <div className="flex items-center gap-1.5 text-white/15">
          <span>□</span><span>□</span><span>□</span>
        </div>
        <div className="flex-1 text-center text-white/30">
          toxshield — v1.0.0
        </div>
      </div>

      {/* Hero */}
      <main className="flex-1 flex items-center justify-center p-6">
        <div className="max-w-lg text-center space-y-8">
          {/* Logo */}
          <div className="space-y-3">
            <h1 className="text-5xl sm:text-6xl font-bold font-mono text-white text-glow tracking-[0.15em]">
              TOXSHIELD
            </h1>
            <div className="w-16 h-px bg-white/20 mx-auto" />
            <p className="text-sm text-white/40 font-mono tracking-[0.1em]">
              FORENSIC BEHAVIORAL ANALYSIS
            </p>
          </div>

          {/* Description */}
          <div className="space-y-4 max-w-md mx-auto">
            <p className="text-white/70 font-mono text-sm leading-relaxed">
              Log a person. Describe their behavior. Get a full AI-powered
              threat profile with toxicity scoring, trait detection, and
              protection strategies.
            </p>
            <p className="text-white/30 font-mono text-xs italic">
              Know who&apos;s toxic before they know you know.
            </p>
          </div>

          {/* Feature grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-left">
            {[
              { icon: '▸', title: 'Threat Profiles', desc: 'AI-generated behavioral analysis with toxicity scores' },
              { icon: '◎', title: 'Track Patterns', desc: 'Log multiple interactions. Watch toxicity evolve' },
              { icon: '●', title: 'Stay Protected', desc: 'Get strategies to protect yourself from toxic behavior' },
            ].map((feature) => (
              <div
                key={feature.title}
                className="p-4 bg-surface border border-white/[0.06] rounded-xl"
              >
                <span className="text-white/50 font-mono text-lg">{feature.icon}</span>
                <h3 className="font-mono text-sm font-bold text-white mt-2 mb-1">
                  {feature.title}
                </h3>
                <p className="text-xs text-white/35 leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>

          {/* CTA */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link
              href="/signup"
              className="px-8 py-3.5 bg-white text-black font-bold rounded-xl font-mono text-sm tracking-wider active:bg-white/90 transition-all glow-subtle min-h-[48px] flex items-center touch-active"
            >
              START ANALYZING →
            </Link>
            <Link
              href="/login"
              className="px-8 py-3.5 border border-white/20 rounded-xl font-mono text-sm text-white active:bg-white/5 transition-colors min-h-[48px] flex items-center touch-active"
            >
              LOGIN
            </Link>
          </div>

          <p className="text-[10px] text-white/20 font-mono">
            ToxShield identifies behavioral patterns. Not a substitute for professional counseling.
          </p>
        </div>
      </main>
    </div>
  );
}
