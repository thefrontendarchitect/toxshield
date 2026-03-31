import type { Metadata } from 'next';
import type { ReactNode } from 'react';

export const metadata: Metadata = {
  title: 'Login',
  description:
    'Sign in to ToxShield to access your forensic behavioral analysis dashboard and threat profiles.',
  alternates: { canonical: 'https://toxshield.in/login' },
};

export default function LoginLayout({ children }: { children: ReactNode }) {
  return <>{children}</>;
}
