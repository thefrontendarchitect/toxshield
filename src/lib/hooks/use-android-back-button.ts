'use client';

import { useEffect, useRef } from 'react';
import { usePathname } from 'next/navigation';

const ROOT_PATHS = ['/dashboard', '/login'];

/**
 * Intercepts the Android hardware back button / back gesture
 * so it navigates within the app instead of closing it.
 *
 * - On root paths (dashboard, login): minimizes the app
 * - On deeper pages: navigates back through browser history
 * - Only active on Android native platform
 */
export function useAndroidBackButton() {
  const pathname = usePathname();
  const pathnameRef = useRef(pathname);
  const lastBackPress = useRef(0);

  useEffect(() => {
    pathnameRef.current = pathname;
  }, [pathname]);

  useEffect(() => {
    // Only run in Capacitor Android
    let handle: { remove: () => Promise<void> } | null = null;

    const setup = async () => {
      try {
        const { Capacitor } = await import('@capacitor/core');
        if (Capacitor.getPlatform() !== 'android') return;

        const { App } = await import('@capacitor/app');

        handle = await App.addListener('backButton', ({ canGoBack }) => {
          const now = Date.now();
          if (now - lastBackPress.current < 300) return;
          lastBackPress.current = now;

          const isRoot = ROOT_PATHS.some(
            (r) => pathnameRef.current === r || pathnameRef.current === `${r}/`
          );

          if (isRoot || !canGoBack) {
            App.minimizeApp();
            return;
          }

          window.history.back();
        });
      } catch {
        // Not in Capacitor environment — ignore
      }
    };

    setup();

    return () => {
      handle?.remove();
    };
  }, []);
}
