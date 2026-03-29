export const FREE_LIMIT = 3;

export interface UsageStatus {
  used: number;
  limit: number;
  bonus: number;
  remaining: number;
  isPro: boolean;
}

export function getMonthStart(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`;
}
