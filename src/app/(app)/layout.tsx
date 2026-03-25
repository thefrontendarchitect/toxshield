'use client';

import { AppHeader } from '@/components/layout/app-header';
import { BottomNav } from '@/components/layout/bottom-nav';
import { usePathname } from 'next/navigation';

const DETAIL_PAGES = ['/people/'];
const PAGE_TITLES: Record<string, string> = {
  '/dashboard': 'CASE_FILE_0821',
  '/analyze': 'CASE_FILE_0821',
  '/people': 'CASE_FILE_0821',
  '/my-insights': 'CASE_FILE_0821',
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
      <AppHeader title={title} showBackButton={isDetailPage} />
      <main className="bg-surface-0 grid-bg pt-[72px] pb-[100px] min-h-screen">
        <div className="px-4 py-6">{children}</div>
      </main>
      <BottomNav />
    </>
  );
}
