'use client';

import { AppHeader } from '@/components/layout/app-header';
import { BottomNav } from '@/components/layout/bottom-nav';
import { usePathname } from 'next/navigation';

const DETAIL_PAGES = ['/people/'];
const PAGE_TITLES: Record<string, string> = {
  '/dashboard': 'COMMAND CENTER',
  '/analyze': 'NEW ANALYSIS',
  '/people': 'SUBJECTS',
  '/settings': 'SETTINGS',
};

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isDetailPage = DETAIL_PAGES.some(
    (p) => pathname.includes(p) && pathname !== '/people'
  );
  const title = PAGE_TITLES[pathname] ?? (isDetailPage ? 'THREAT PROFILE' : 'TOXSHIELD');

  return (
    <>
      <AppHeader title={title} showBackButton={isDetailPage} />
      <main className="bg-black pt-[72px] pb-[100px]">
        <div className="px-4 py-6">{children}</div>
      </main>
      <BottomNav />
    </>
  );
}
