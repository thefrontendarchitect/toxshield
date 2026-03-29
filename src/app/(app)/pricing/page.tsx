'use client';

import { motion } from 'framer-motion';

const tiers = [
  {
    name: 'FREE',
    price: '$0',
    period: 'forever',
    features: [
      '3 analyses per month',
      'Basic share cards',
      'Environment health tracking',
      'My Mirror insights',
      'Weekly streaks & badges',
    ],
    cta: 'CURRENT PLAN',
    ctaStyle: 'border border-surface-3 text-text-secondary',
    disabled: true,
  },
  {
    name: 'PRO',
    price: '$4.99',
    period: '/month',
    features: [
      'Unlimited analyses',
      'Premium share cards (no watermark)',
      'Monthly Wrapped reports',
      'Priority AI processing',
      'Trend graphs & historical data',
      'Export to PDF',
      'Email & SMS input parsing',
    ],
    cta: 'JOIN WAITLIST',
    ctaStyle: 'bg-neon-cyan text-surface-0 font-bold',
    disabled: false,
    highlighted: true,
  },
  {
    name: 'TEAM',
    price: '$14.99',
    period: '/month',
    features: [
      'Everything in Pro',
      'Shared profiles',
      'Team dashboard',
      'Admin controls',
      'Priority support',
    ],
    cta: 'COMING SOON',
    ctaStyle: 'border border-surface-3 text-text-secondary',
    disabled: true,
  },
];

export default function PricingPage() {
  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="text-center space-y-2">
        <span className="tag-badge">UPGRADE</span>
        <h1 className="hero-title text-3xl">PRICING</h1>
        <p className="font-mono text-xs text-text-secondary">
          Unlock unlimited forensic intelligence.
        </p>
      </motion.div>

      <div className="space-y-4">
        {tiers.map((tier, i) => (
          <motion.div
            key={tier.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className={`arcane-glass p-5 space-y-4 ${
              tier.highlighted ? 'border border-neon-cyan/20' : ''
            }`}
          >
            <div className="flex items-baseline justify-between">
              <div>
                <p className="font-mono text-sm font-bold text-text-primary uppercase tracking-wider">
                  {tier.name}
                </p>
                {tier.highlighted && (
                  <span className="font-mono text-[9px] text-neon-cyan uppercase tracking-wider">
                    Most Popular
                  </span>
                )}
              </div>
              <div className="text-right">
                <span className="font-mono text-2xl font-black italic text-text-primary">
                  {tier.price}
                </span>
                <span className="font-mono text-xs text-text-secondary">{tier.period}</span>
              </div>
            </div>

            <ul className="space-y-2">
              {tier.features.map((feature) => (
                <li key={feature} className="flex items-center gap-2">
                  <span className="text-neon-cyan text-xs">&#x2713;</span>
                  <span className="font-mono text-xs text-text-secondary">{feature}</span>
                </li>
              ))}
            </ul>

            <button
              type="button"
              disabled={tier.disabled}
              className={`w-full py-3 rounded-xl font-mono text-xs tracking-wider min-h-[44px] touch-active transition-all ${tier.ctaStyle} ${
                tier.disabled ? 'opacity-40 cursor-not-allowed' : 'active:opacity-80'
              }`}
            >
              {tier.cta}
            </button>
          </motion.div>
        ))}
      </div>

      <p className="text-center font-mono text-[10px] text-text-secondary/40">
        Stripe payments coming soon. Join the waitlist to be notified.
      </p>
    </div>
  );
}
