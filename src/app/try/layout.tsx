import type { Metadata } from 'next';
import type { ReactNode } from 'react';

export const metadata: Metadata = {
  title: 'Try ToxShield — Free Demo',
  description:
    'Try ToxShield for free. Describe a behavior and get an instant AI-powered toxicity analysis with threat profile.',
  alternates: { canonical: 'https://toxshield.in/try' },
};

export default function TryLayout({ children }: { children: ReactNode }) {
  return <>{children}</>;
}
