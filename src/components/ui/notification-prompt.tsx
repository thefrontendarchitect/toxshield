'use client';

import { useState, useEffect } from 'react';

const VAPID_PUBLIC_KEY = process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY ?? '';
const DISMISSED_KEY = 'toxshield_notification_prompt_dismissed';

export function NotificationPrompt() {
  const [show, setShow] = useState(false);
  const [registering, setRegistering] = useState(false);

  useEffect(() => {
    // Only show if: browser supports notifications, not yet granted, not dismissed, VAPID key exists
    if (
      !VAPID_PUBLIC_KEY ||
      typeof window === 'undefined' ||
      !('Notification' in window) ||
      !('serviceWorker' in navigator) ||
      Notification.permission !== 'default' ||
      localStorage.getItem(DISMISSED_KEY)
    ) {
      return;
    }
    setShow(true);
  }, []);

  if (!show) return null;

  const handleEnable = async () => {
    setRegistering(true);
    try {
      const permission = await Notification.requestPermission();
      if (permission !== 'granted') {
        handleDismiss();
        return;
      }

      // Register service worker
      const registration = await navigator.serviceWorker.register('/sw.js');
      await navigator.serviceWorker.ready;

      // Subscribe to push
      const applicationServerKey = urlBase64ToUint8Array(VAPID_PUBLIC_KEY);
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: applicationServerKey.buffer as ArrayBuffer,
      });

      const json = subscription.toJSON();

      // Send subscription to server
      await fetch('/api/notifications/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          endpoint: json.endpoint,
          keys: json.keys,
        }),
      });

      setShow(false);
    } catch (err) {
      console.error('[notifications] Failed to register:', err);
      handleDismiss();
    } finally {
      setRegistering(false);
    }
  };

  const handleDismiss = () => {
    localStorage.setItem(DISMISSED_KEY, 'true');
    setShow(false);
  };

  return (
    <div className="arcane-glass p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="font-mono text-xs font-bold text-text-primary mb-1">
            Stay on track
          </p>
          <p className="font-mono text-[10px] text-text-secondary leading-relaxed">
            Get streak reminders and weekly insights. Max 3 per week.
          </p>
        </div>
        <button
          type="button"
          onClick={handleDismiss}
          className="shrink-0 font-mono text-xs text-text-secondary active:text-text-primary"
          aria-label="Dismiss"
        >
          &times;
        </button>
      </div>
      <button
        type="button"
        onClick={handleEnable}
        disabled={registering}
        className="mt-3 w-full py-2.5 bg-neon-cyan/10 border border-neon-cyan/15 rounded-lg font-mono text-xs text-neon-cyan active:bg-neon-cyan/20 transition-colors touch-active disabled:opacity-50"
      >
        {registering ? 'Enabling...' : 'Enable Notifications'}
      </button>
    </div>
  );
}

function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; i++) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}
