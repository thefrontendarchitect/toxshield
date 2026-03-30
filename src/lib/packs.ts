export const PACKS = {
  daily_boost: {
    name: 'Daily Boost',
    analyses: 10,
    duration_days: 1,
    daily_limit: 10,
    price_usd: '$1.29',
    price_inr: '₹99',
    price_cents: 129,
    price_paise: 9900,
  },
  weekly_intel: {
    name: 'Weekly Intel',
    analyses: 21,
    duration_days: 7,
    daily_limit: 3,
    price_usd: '$2.49',
    price_inr: '₹199',
    price_cents: 249,
    price_paise: 19900,
  },
  monthly_pro: {
    name: 'Monthly Pro',
    analyses: 9999,
    duration_days: 30,
    daily_limit: 9999,
    price_usd: '$4.99',
    price_inr: '₹399',
    price_cents: 499,
    price_paise: 39900,
  },
} as const;

export type PackType = keyof typeof PACKS;

export function formatPackExpiry(expiresAt: string): string {
  const ms = new Date(expiresAt).getTime() - Date.now();
  const hours = Math.floor(ms / (1000 * 60 * 60));
  if (hours < 1) return 'Expires soon';
  if (hours < 24) return `${hours}h remaining`;
  const days = Math.ceil(ms / (1000 * 60 * 60 * 24));
  return `${days}d remaining`;
}
