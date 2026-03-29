'use client';

import { AuroraBackground, hashString } from '@/components/ui/aurora-background';
import { usePathname } from 'next/navigation';

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div className="flex flex-col min-h-screen bg-surface-0 relative">
      <AuroraBackground seed={hashString(pathname)} />
      <main className="flex-1 flex items-center justify-center p-4 relative z-10">
        {children}
      </main>
    </div>
  );
}
