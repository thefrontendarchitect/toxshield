'use client';

import { useEffect, useRef } from 'react';

/**
 * Tracks Capacitor app foreground/background lifecycle.
 * Only active on native platforms (iOS/Android).
 */
export function useAppLifecycle() {
  const listenerRef = useRef<{ remove: () => Promise<void> } | null>(null);

  useEffect(() => {
    const setup = async () => {
      try {
        const { Capacitor } = await import('@capacitor/core');
        if (!Capacitor.isNativePlatform()) return;

        const { App } = await import('@capacitor/app');

        const handle = await App.addListener('appStateChange', ({ isActive }) => {
          if (process.env.NODE_ENV === 'development') {
            console.log(`[ToxShield] App ${isActive ? 'foregrounded' : 'backgrounded'}`);
          }
        });

        listenerRef.current = handle;
      } catch {
        // Not in Capacitor environment
      }
    };

    setup();

    return () => {
      listenerRef.current?.remove();
    };
  }, []);
}
