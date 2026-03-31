import type { Metadata } from 'next';
import type { ReactNode } from 'react';

export const metadata: Metadata = {
  title: 'Sign Up',
  description:
    'Create your free ToxShield account. AI-powered toxic behavior detection and relationship analysis.',
  alternates: { canonical: 'https://toxshield.in/signup' },
};

export default function SignupLayout({ children }: { children: ReactNode }) {
  return <>{children}</>;
}
