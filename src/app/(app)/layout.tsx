'use client';

import { AppHeader } from '@/components/layout/app-header';
import { BottomNav } from '@/components/layout/bottom-nav';
import { AuroraBackground, hashString } from '@/components/ui/aurora-background';
import { usePathname } from 'next/navigation';

const DETAIL_PAGES = ['/people/'];
const PAGE_TITLES: Record<string, string> = {
  '/dashboard': 'CASE_FILE_0821',
  '/analyze': 'CASE_FILE_0821',
  '/people': 'CASE_FILE_0821',
  '/my-insights': 'CASE_FILE_0821',
  '/pulse': 'COMMUNITY_PULSE',
  '/wrapped': 'YOUR_WRAPPED',
  '/settings': 'SETTINGS',
};

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isDetailPage = DETAIL_PAGES.some(
    (p) => pathname.includes(p) && pathname !== '/people'
  );
  const title = PAGE_TITLES[pathname] ?? (isDetailPage ? 'CASE_FILE_0821' : 'TOXSHIELD');

  return (
    <>
      <AuroraBackground seed={hashString(pathname)} />
      <AppHeader title={title} showBackButton={isDetailPage} />
      <main className="bg-surface-0/60 grid-bg pt-[72px] pb-[100px] min-h-screen relative">
        <div className="px-4 py-6">{children}</div>
      </main>
      <BottomNav />
    </>
  );
}
