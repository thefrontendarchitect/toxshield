'use client';

import { ReactNode, useEffect } from 'react';
import { Capacitor } from '@capacitor/core';
import { useKeyboardOffset } from '@/lib/hooks/use-keyboard-offset';
import { useAndroidBackButton } from '@/lib/hooks/use-android-back-button';
import { useAppLifecycle } from '@/lib/hooks/use-app-lifecycle';
import { useSafeAreaInsets } from '@/lib/hooks/use-safe-area-insets';
import { useUtmTracking } from '@/hooks/use-utm-tracking';

interface AppProvidersProps {
  children: ReactNode;
}

export function AppProviders({ children }: AppProvidersProps) {
  useKeyboardOffset();
  useAndroidBackButton();
  useAppLifecycle();
  useSafeAreaInsets();
  useUtmTracking();

  useEffect(() => {
    if (!Capacitor.isNativePlatform()) return;

    (async () => {
      try {
        const { StatusBar, Style } = await import('@capacitor/status-bar');
        await StatusBar.setStyle({ style: Style.Dark });
        await StatusBar.setBackgroundColor({ color: '#080519' });
      } catch (error) {
        if (Capacitor.isNativePlatform()) {
          console.error('[ToxShield] StatusBar initialization failed:', error);
        }
      }
    })();
  }, []);

  return <>{children}</>;
}
