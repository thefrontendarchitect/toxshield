'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Spinner } from '@/components/ui/spinner';
import { useRazorpayScript } from '@/hooks/use-razorpay-script';

type Gateway = 'stripe' | 'razorpay';

const packs = [
  {
    id: null,
    name: 'FREE',
    description: '3 analyses per month',
    features: [
      '3 analyses / month',
      'Basic share cards',
      'Environment health tracking',
      'My Mirror insights',
      'Weekly streaks & badges',
    ],
    price_usd: '$0',
    price_inr: '₹0',
    period: 'forever',
    cta: 'CURRENT PLAN',
    disabled: true,
  },
  {
    id: 'daily_boost',
    name: 'DAILY BOOST',
    description: '10 analyses in 24 hours',
    features: [
      '10 analyses in one day',
      'Deep-dive a single person',
      'All input modes (text, WhatsApp, Slack)',
      'Full threat profiles & share cards',
    ],
    price_usd: '$1.29',
    price_inr: '₹99',
    period: 'one-time',
    cta: 'BUY NOW',
    disabled: false,
    highlighted: false,
  },
  {
    id: 'weekly_intel',
    name: 'WEEKLY INTEL',
    description: '3 analyses/day for 7 days',
    features: [
      '3 analyses per day for 7 days',
      '21 total analyses',
      'Map your entire social circle',
      'All input modes + full profiles',
    ],
    price_usd: '$2.49',
    price_inr: '₹199',
    period: 'one-time',
    cta: 'BUY NOW',
    disabled: false,
    highlighted: true,
  },
  {
    id: 'monthly_pro',
    name: 'MONTHLY PRO',
    description: 'Unlimited analyses for 30 days',
    features: [
      'Unlimited analyses for 30 days',
      'All input modes (text, WhatsApp, Slack)',
      'Full threat profiles & share cards',
      'Priority AI processing',
      'My Mirror insights & environment health',
    ],
    price_usd: '$4.99',
    price_inr: '₹399',
    period: 'one-time',
    cta: 'BUY NOW',
    disabled: false,
    highlighted: false,
  },
];

export default function PricingPage() {
  const [gateway, setGateway] = useState<Gateway>('razorpay');
  const [loadingPack, setLoadingPack] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { isLoaded: razorpayLoaded } = useRazorpayScript();

  const handleStripe = async (packId: string) => {
    setLoadingPack(packId);
    setError(null);
    try {
      const res = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pack: packId }),
      });
      const data = await res.json();
      if (data.url) {
        router.push(data.url);
      } else {
        setError(data.error || 'Failed to start checkout. Please try again.');
        setLoadingPack(null);
      }
    } catch {
      setError('Network error. Please check your connection and try again.');
      setLoadingPack(null);
    }
  };

  const handleRazorpay = async (packId: string) => {
    if (!razorpayLoaded) return;
    setLoadingPack(packId);
    setError(null);

    try {
      const res = await fetch('/api/checkout/razorpay', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pack: packId }),
      });
      const data = await res.json();

      if (!data.order_id) {
        setError(data.error || 'Failed to create order. Please try again.');
        setLoadingPack(null);
        return;
      }

      const rzp = new window.Razorpay({
        key: data.key_id,
        amount: data.amount,
        currency: data.currency,
        name: data.name,
        description: data.description,
        order_id: data.order_id,
        prefill: data.prefill,
        theme: { color: '#00b4ff' }, // neon-cyan — Arcane Hextech Core
        handler: async (response: { razorpay_order_id: string; razorpay_payment_id: string; razorpay_signature: string }) => {
          try {
            const verifyRes = await fetch('/api/checkout/razorpay/verify', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(response),
            });
            const verifyData = await verifyRes.json();
            if (verifyData.success) {
              router.push('/checkout/success');
            } else {
              setError('Payment verification failed. Please contact support.');
              setLoadingPack(null);
            }
          } catch {
            setError('Payment verification error. Please contact support.');
            setLoadingPack(null);
          }
        },
        modal: {
          ondismiss: () => setLoadingPack(null),
        },
      });

      rzp.open();
    } catch {
      setError('Failed to open payment gateway. Please try again.');
      setLoadingPack(null);
    }
  };

  const handleBuy = (packId: string) => {
    if (gateway === 'stripe') {
      handleStripe(packId);
    } else {
      handleRazorpay(packId);
    }
  };

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="text-center space-y-2">
        <span className="tag-badge">UPGRADE</span>
        <h1 className="hero-title text-3xl">PRICING</h1>
        <p className="font-mono text-xs text-text-secondary">
          Buy analysis packs. No subscriptions.
        </p>
      </motion.div>

      {/* Error display */}
      {error && (
        <div className="arcane-glass border border-neon-magenta/20 p-3">
          <p className="font-mono text-xs text-neon-magenta text-center">{error}</p>
        </div>
      )}

      {/* Gateway toggle */}
      <div role="group" aria-label="Payment gateway" className="flex items-center justify-center gap-1 p-1 bg-surface-1 rounded-lg border border-surface-3">
        <button
          type="button"
          onClick={() => setGateway('razorpay')}
          aria-pressed={gateway === 'razorpay'}
          className={`flex-1 py-2 rounded-md font-mono text-[10px] uppercase tracking-wider transition-all ${
            gateway === 'razorpay'
              ? 'bg-neon-cyan text-surface-0 font-bold'
              : 'text-text-secondary active:text-text-primary'
          }`}
        >
          UPI / Razorpay
        </button>
        <button
          type="button"
          onClick={() => setGateway('stripe')}
          aria-pressed={gateway === 'stripe'}
          className={`flex-1 py-2 rounded-md font-mono text-[10px] uppercase tracking-wider transition-all ${
            gateway === 'stripe'
              ? 'bg-neon-cyan text-surface-0 font-bold'
              : 'text-text-secondary active:text-text-primary'
          }`}
        >
          Card / Stripe
        </button>
      </div>

      <div className="space-y-4">
        {packs.map((pack, i) => (
          <motion.div
            key={pack.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className={`arcane-glass p-5 space-y-4 ${
              pack.highlighted ? 'border border-neon-cyan/20' : ''
            }`}
          >
            <div className="flex items-baseline justify-between">
              <div>
                <p className="font-mono text-sm font-bold text-text-primary uppercase tracking-wider">
                  {pack.name}
                </p>
                {pack.highlighted && (
                  <span className="font-mono text-[9px] text-neon-cyan uppercase tracking-wider">
                    Best Value
                  </span>
                )}
                <p className="font-mono text-[10px] text-text-secondary mt-0.5">
                  {pack.description}
                </p>
              </div>
              <div className="text-right">
                <span className="font-mono text-2xl font-black italic text-text-primary">
                  {gateway === 'razorpay' ? pack.price_inr : pack.price_usd}
                </span>
                <span className="font-mono text-xs text-text-secondary">/{pack.period}</span>
                {pack.id && (
                  <p className="font-mono text-[10px] text-text-secondary">
                    {gateway === 'razorpay' ? pack.price_usd : pack.price_inr}
                  </p>
                )}
              </div>
            </div>

            <ul className="space-y-2">
              {pack.features.map((feature) => (
                <li key={feature} className="flex items-center gap-2">
                  <span className="text-neon-cyan text-xs">&#x2713;</span>
                  <span className="font-mono text-xs text-text-secondary">{feature}</span>
                </li>
              ))}
            </ul>

            <button
              type="button"
              disabled={pack.disabled || loadingPack === pack.id}
              onClick={() => pack.id && handleBuy(pack.id)}
              className={`w-full py-3 rounded-xl font-mono text-xs tracking-wider min-h-[44px] touch-active transition-all ${
                pack.disabled
                  ? 'border border-surface-3 text-text-secondary opacity-40 cursor-not-allowed'
                  : 'bg-neon-cyan text-surface-0 font-bold active:bg-neon-cyan/90'
              }`}
            >
              {pack.id && loadingPack === pack.id ? (
                <span className="flex items-center justify-center gap-2">
                  <Spinner />
                  {gateway === 'stripe' ? 'REDIRECTING...' : 'LOADING...'}
                </span>
              ) : pack.cta}
            </button>
          </motion.div>
        ))}
      </div>

      <p className="text-center font-mono text-[10px] text-text-secondary/40">
        {gateway === 'stripe'
          ? 'Secure payments via Stripe. Packs activate immediately.'
          : 'Secure payments via Razorpay. UPI, cards, net banking accepted.'}
      </p>
    </div>
  );
}
