'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: '◇' },
  { href: '/analyze', label: 'Analyze', icon: '⊕' },
  { href: '/people', label: 'People', icon: '◎' },
  { href: '/my-insights', label: 'Mirror', icon: '◈' },
  { href: '/settings', label: 'Settings', icon: '⚙' },
];

export function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-white/[0.06] bg-surface-0/95 backdrop-blur-md pb-safe">
      <ul className="flex h-16 items-center justify-around">
        {navItems.map((item) => {
          const isActive =
            pathname === item.href || pathname?.startsWith(item.href + '/');

          return (
            <li key={item.href}>
              <Link
                href={item.href}
                aria-current={isActive ? 'page' : undefined}
                className="relative flex min-h-[44px] min-w-[44px] flex-col items-center justify-center gap-0.5 px-3 py-2 rounded-xl transition-all active:bg-white/5"
              >
                <span
                  aria-hidden="true"
                  className={`text-lg transition-all ${
                    isActive ? 'text-white' : 'text-white/30'
                  }`}
                >
                  {item.icon}
                </span>
                <span
                  className={`text-[14px] font-mono transition-all ${
                    isActive
                      ? 'text-white font-bold'
                      : 'text-white/30'
                  }`}
                >
                  {item.label}
                </span>
                {isActive && (
                  <div className="absolute -top-0.5 left-3 right-3 h-[2px] bg-white rounded-full" />
                )}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
