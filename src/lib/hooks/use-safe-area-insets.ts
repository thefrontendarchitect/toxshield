'use client';

import { useEffect } from 'react';
import { Capacitor } from '@capacitor/core';

export function useSafeAreaInsets(): void {
  useEffect(() => {
    if (!Capacitor.isNativePlatform()) return;

    let cancelled = false;
    let listener: { remove: () => void } | undefined;

    (async () => {
      try {
        const { SafeArea } = await import('capacitor-plugin-safe-area');

        const { insets } = await SafeArea.getSafeAreaInsets();
        if (cancelled) return;

        const root = document.documentElement;
        root.style.setProperty('--safe-area-inset-top', `${insets.top}px`);
        root.style.setProperty('--safe-area-inset-bottom', `${insets.bottom}px`);
        root.style.setProperty('--safe-area-inset-left', `${insets.left}px`);
        root.style.setProperty('--safe-area-inset-right', `${insets.right}px`);

        const handle = await SafeArea.addListener(
          'safeAreaChanged',
          ({ insets: newInsets }) => {
            root.style.setProperty('--safe-area-inset-top', `${newInsets.top}px`);
            root.style.setProperty('--safe-area-inset-bottom', `${newInsets.bottom}px`);
            root.style.setProperty('--safe-area-inset-left', `${newInsets.left}px`);
            root.style.setProperty('--safe-area-inset-right', `${newInsets.right}px`);
          }
        );

        if (cancelled) {
          handle.remove();
          return;
        }
        listener = handle;
      } catch (error) {
        console.error('Failed to initialize safe area insets:', error);
      }
    })();

    return () => {
      cancelled = true;
      listener?.remove();
    };
  }, []);
}
