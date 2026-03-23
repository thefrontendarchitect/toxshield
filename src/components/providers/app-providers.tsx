'use client';

import { ReactNode } from 'react';
import { useKeyboardOffset } from '@/lib/hooks/use-keyboard-offset';
import { useAndroidBackButton } from '@/lib/hooks/use-android-back-button';
import { useAppLifecycle } from '@/lib/hooks/use-app-lifecycle';

interface AppProvidersProps {
  children: ReactNode;
}

export function AppProviders({ children }: AppProvidersProps) {
  useKeyboardOffset();
  useAndroidBackButton();
  useAppLifecycle();

  return <>{children}</>;
}
