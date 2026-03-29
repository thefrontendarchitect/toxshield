'use client';

import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import { ShieldIcon } from '@/components/ui/dossier-icons';

interface PaywallModalProps {
  isOpen: boolean;
  onClose: () => void;
  used: number;
  limit: number;
}

export function PaywallModal({ isOpen, onClose, used, limit }: PaywallModalProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[100] flex items-center justify-center px-4"
        >
          {/* Backdrop */}
          <div className="absolute inset-0 bg-surface-0/80 backdrop-blur-sm" onClick={onClose} />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            role="dialog"
            aria-modal="true"
            aria-labelledby="paywall-title"
            className="relative w-full max-w-sm arcane-glass p-6 space-y-5 rounded-2xl border border-neon-cyan/15"
          >
            <div className="text-center space-y-2">
              <ShieldIcon size={32} className="mx-auto text-neon-cyan/40" />
              <h2 id="paywall-title" className="font-mono text-lg font-bold text-text-primary uppercase">
                Analysis Limit Reached
              </h2>
              <p className="font-mono text-xs text-text-secondary">
                You&apos;ve used {used} of {limit} free analyses this month.
              </p>
            </div>

            {/* Usage bar */}
            <div className="w-full h-2 bg-surface-2 rounded-full overflow-hidden">
              <div
                className="h-full bg-neon-magenta rounded-full"
                style={{ width: '100%' }}
              />
            </div>

            {/* Upgrade CTA */}
            <Link
              href="/pricing"
              className="block w-full py-3.5 bg-neon-cyan text-surface-0 font-bold rounded-xl font-mono text-sm tracking-wider text-center active:opacity-90 transition-all min-h-[48px] touch-active"
            >
              UPGRADE TO PRO — UNLIMITED
            </Link>

            {/* Referral hint */}
            <p className="text-center font-mono text-[10px] text-text-secondary">
              Or invite a friend for bonus analyses
            </p>

            {/* Dismiss */}
            <button
              type="button"
              onClick={onClose}
              className="w-full py-2 font-mono text-xs text-text-secondary active:text-text-primary transition-colors touch-active"
            >
              MAYBE LATER
            </button>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
