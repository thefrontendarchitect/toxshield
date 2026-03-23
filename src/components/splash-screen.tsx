'use client';

import { useEffect, useState } from 'react';

interface SplashScreenProps {
  onComplete?: () => void;
  delay?: number;
}

export function SplashScreen({ onComplete, delay = 1500 }: SplashScreenProps) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      onComplete?.();
    }, delay);

    const dismissNative = async () => {
      try {
        const { SplashScreen } = await import('@capacitor/splash-screen');
        await SplashScreen.hide();
      } catch {
        // Not in Capacitor
      }
    };
    dismissNative();

    return () => clearTimeout(timer);
  }, [delay, onComplete]);

  if (!visible) return null;

  return (
    <div className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-black">
      <div className="text-center space-y-4">
        <h1 className="text-3xl font-bold font-mono text-white text-glow tracking-[0.3em]">
          TOXSHIELD
        </h1>
        <p className="text-xs font-mono text-white/40 tracking-[0.15em] uppercase">
          Behavioral Threat Analysis
        </p>
        <div className="flex items-center justify-center gap-1.5 mt-6">
          <span className="w-1 h-1 rounded-full bg-white animate-pulse" />
          <span className="w-1 h-1 rounded-full bg-white animate-pulse [animation-delay:200ms]" />
          <span className="w-1 h-1 rounded-full bg-white animate-pulse [animation-delay:400ms]" />
        </div>
      </div>
    </div>
  );
}
