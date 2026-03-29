'use client';

import { useEffect, useState } from 'react';

interface ReferralData {
  referral_code: string;
  referral_url: string;
  stats: {
    total: number;
    completed: number;
    pending: number;
    bonus_earned: number;
  };
}

export function ReferralCard() {
  const [data, setData] = useState<ReferralData | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetch('/api/referrals')
      .then((r) => r.json())
      .then(setData)
      .catch(console.error);
  }, []);

  if (!data) return null;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(data.referral_url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback
      const input = document.createElement('input');
      input.value = data.referral_url;
      document.body.appendChild(input);
      input.select();
      document.execCommand('copy');
      document.body.removeChild(input);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'ToxShield — Analyze Your Circle',
          text: 'I use ToxShield to analyze toxic patterns. Try it free:',
          url: data.referral_url,
        });
      } catch (err) {
        if (err instanceof Error && err.name !== 'AbortError') {
          handleCopy();
        }
      }
    } else {
      handleCopy();
    }
  };

  return (
    <div className="arcane-glass p-4 space-y-3">
      <p className="label-section">INVITE FRIENDS</p>
      <p className="font-mono text-[10px] text-text-secondary">
        Both you and your friend get bonus analyses.
      </p>

      {/* Referral code display */}
      <div className="flex items-center gap-2">
        <div className="flex-1 bg-surface-2 rounded-lg px-3 py-2.5 font-mono text-sm font-bold text-neon-cyan tracking-[0.15em] text-center">
          {data.referral_code}
        </div>
        <button
          type="button"
          onClick={handleCopy}
          className="shrink-0 px-3 py-2.5 border border-neon-cyan/15 rounded-lg font-mono text-[10px] text-text-primary active:bg-neon-cyan/5 transition-colors touch-active"
        >
          {copied ? 'COPIED!' : 'COPY'}
        </button>
      </div>

      {/* Share button */}
      <button
        type="button"
        onClick={handleShare}
        className="w-full py-3 bg-neon-cyan/10 border border-neon-cyan/15 rounded-xl font-mono text-xs text-neon-cyan active:bg-neon-cyan/20 transition-colors touch-active"
      >
        SHARE INVITE LINK
      </button>

      {/* Stats */}
      {data.stats.total > 0 && (
        <div className="flex justify-between pt-2 border-t border-surface-3">
          <div className="text-center">
            <p className="font-mono text-lg font-bold text-text-primary">{data.stats.completed}</p>
            <p className="font-mono text-[9px] text-text-secondary">Joined</p>
          </div>
          <div className="text-center">
            <p className="font-mono text-lg font-bold text-text-primary">{data.stats.pending}</p>
            <p className="font-mono text-[9px] text-text-secondary">Pending</p>
          </div>
          <div className="text-center">
            <p className="font-mono text-lg font-bold text-neon-cyan">{data.stats.bonus_earned}</p>
            <p className="font-mono text-[9px] text-text-secondary">Bonus Earned</p>
          </div>
        </div>
      )}
    </div>
  );
}
