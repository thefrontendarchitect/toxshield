'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { createClient } from '@/lib/supabase/client';
import { useRouter } from 'next/navigation';

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: '>' },
  { href: '/analyze', label: 'New Analysis', icon: '+' },
  { href: '/people', label: 'People', icon: '#' },
  { href: '/my-insights', label: 'My Mirror', icon: '◈' },
  { href: '/settings', label: 'Settings', icon: '*' },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  const handleSignOut = async () => {
    const supabase = createClient();
    await supabase.auth.signOut();
    router.push('/login');
  };

  return (
    <aside className="w-56 arcane-glass border-r border-neon-cyan/[0.06] flex flex-col font-mono text-sm">
      {/* Logo */}
      <div className="p-4 border-b border-neon-cyan/[0.06]">
        <h1 className="text-lg font-bold text-text-primary text-glow-subtle tracking-wider">
          TOXSHIELD
        </h1>
        <p className="text-[14px] text-text-secondary mt-0.5">
          BEHAVIORAL THREAT ANALYSIS
        </p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-2 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-2 px-3 py-2 rounded transition-colors ${
                isActive
                  ? 'bg-neon-cyan/10 text-neon-cyan'
                  : 'text-text-secondary hover:text-text-primary hover:bg-neon-cyan/5'
              }`}
            >
              <span className={isActive ? 'text-neon-cyan' : 'text-text-secondary'}>
                {item.icon}
              </span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Sign out */}
      <div className="p-2 border-t border-neon-cyan/[0.06]">
        <button
          onClick={handleSignOut}
          className="w-full flex items-center gap-2 px-3 py-2 rounded text-text-secondary hover:text-neon-magenta hover:bg-neon-magenta/5 transition-colors"
        >
          <span>{'<'}</span>
          Sign Out
        </button>
      </div>
    </aside>
  );
}
