'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { FingerprintIcon, BrainIcon, EyeIcon, DocumentIcon } from '@/components/ui/dossier-icons';

const navItems = [
  { href: '/dashboard', label: 'DOSSIER', Icon: FingerprintIcon },
  { href: '/analyze', label: 'ANALYSIS', Icon: BrainIcon },
  { href: '/people', label: 'EVIDENCE', Icon: EyeIcon },
  { href: '/my-insights', label: 'FILES', Icon: DocumentIcon },
];

export function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-white/[0.06] bg-surface-0 pb-safe">
      <ul className="flex h-16 items-center justify-around">
        {navItems.map((item) => {
          const isActive =
            pathname === item.href || pathname?.startsWith(item.href + '/');

          return (
            <li key={item.href}>
              <Link
                href={item.href}
                aria-current={isActive ? 'page' : undefined}
                className="relative flex min-h-[44px] min-w-[56px] flex-col items-center justify-center gap-1 px-3 py-2 transition-all active:opacity-70"
              >
                <div
                  className={`flex items-center justify-center w-8 h-8 rounded-lg transition-all ${
                    isActive ? 'bg-white' : ''
                  }`}
                >
                  <item.Icon
                    size={18}
                    className={isActive ? 'text-black' : 'text-white/30'}
                  />
                </div>
                <span
                  className={`font-mono text-[10px] uppercase tracking-[0.15em] transition-all ${
                    isActive ? 'text-white font-bold' : 'text-white/30'
                  }`}
                >
                  {item.label}
                </span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
