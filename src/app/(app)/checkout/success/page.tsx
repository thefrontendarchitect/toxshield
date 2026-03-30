'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { ShieldIcon } from '@/components/ui/dossier-icons';
import { Spinner } from '@/components/ui/spinner';
import { PACKS, formatPackExpiry } from '@/lib/packs';
import type { PurchaseStatus } from '@/types/database';

export default function CheckoutSuccessPage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center min-h-[60vh]"><Spinner /></div>}>
      <CheckoutSuccessContent />
    </Suspense>
  );
}

function CheckoutSuccessContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const sessionId = searchParams.get('session_id');
  const [purchase, setPurchase] = useState<PurchaseStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!sessionId) {
      router.replace('/pricing');
      return;
    }

    let cancelled = false;
    let timeoutId: ReturnType<typeof setTimeout>;
    let attempts = 0;
    const maxAttempts = 3;

    async function verify() {
      if (cancelled) return;
      try {
        const res = await fetch(`/api/purchases/verify?session_id=${sessionId}`);
        if (!res.ok) {
          if (res.status === 404) {
            if (!cancelled) router.replace('/pricing');
            return;
          }
          throw new Error('Verification failed');
        }
        const data: PurchaseStatus = await res.json();
        if (!cancelled) setPurchase(data);

        if (data.status === 'pending' && attempts < maxAttempts) {
          attempts++;
          timeoutId = setTimeout(verify, 2000);
          return;
        }
        if (!cancelled) setLoading(false);
      } catch {
        if (!cancelled) setLoading(false);
      }
    }

    verify();
    return () => { cancelled = true; clearTimeout(timeoutId); };
  }, [sessionId, router]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-4 px-4">
        <Spinner />
        <p className="font-mono text-sm text-text-secondary">Verifying your purchase...</p>
      </div>
    );
  }

  if (!purchase || purchase.status === 'failed') {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6 px-4">
        <p className="font-mono text-sm text-neon-magenta">Something went wrong with your purchase.</p>
        <Link href="/pricing" className="font-mono text-xs text-neon-cyan active:text-neon-cyan/80 transition-colors">
          Back to Pricing
        </Link>
      </div>
    );
  }

  if (purchase.status === 'pending') {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6 px-4">
        <Spinner />
        <div className="space-y-2">
          <h1 className="font-mono text-lg font-bold text-text-primary uppercase">Processing Payment</h1>
          <p className="font-mono text-sm text-text-secondary max-w-xs">
            Your payment is being processed. This usually takes a few seconds. Check back shortly.
          </p>
        </div>
        <Link href="/dashboard" className="font-mono text-xs text-neon-cyan active:text-neon-cyan/80 transition-colors">
          Go to Dashboard
        </Link>
      </div>
    );
  }

  const pack = PACKS[purchase.pack_type];

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6 px-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        className="space-y-4"
      >
        <ShieldIcon size={48} className="mx-auto text-neon-mint" aria-hidden="true" />
        <h1 className="font-mono text-xl font-bold text-text-primary uppercase">
          Pack Activated
        </h1>
        <div className="arcane-glass p-4 space-y-2 max-w-xs mx-auto">
          <p className="font-mono text-sm font-bold text-neon-cyan uppercase tracking-wider">
            {pack.name}
          </p>
          <p className="font-mono text-xs text-text-secondary">
            {purchase.analyses_remaining} / {purchase.analyses_granted} analyses remaining
          </p>
          <p className="font-mono text-[10px] text-dim">
            {formatPackExpiry(purchase.expires_at)}
          </p>
        </div>
      </motion.div>

      <Link
        href="/analyze"
        className="px-8 py-3.5 bg-neon-cyan text-surface-0 font-bold rounded-xl font-mono text-xs tracking-wider min-h-[48px] touch-active transition-all active:bg-neon-cyan/90"
      >
        START ANALYZING
      </Link>

      <Link
        href="/dashboard"
        className="font-mono text-xs text-text-secondary active:text-text-primary transition-colors"
      >
        Back to Dashboard
      </Link>
    </div>
  );
}
