'use client';

import { useEffect, useCallback, useRef } from 'react';
import { track } from '@vercel/analytics';

function getDeviceCategory(): string {
  const w = window.innerWidth;
  if (w < 768) return 'mobile';
  if (w < 1024) return 'tablet';
  return 'desktop';
}

/**
 * Track when an element matching `selector` becomes 50% visible.
 * Uses selector directly — no refs, no race conditions.
 */
function useTrackVisible(selector: string, eventName: string) {
  useEffect(() => {
    const el = document.querySelector(selector);
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          track(eventName);
          observer.disconnect();
        }
      },
      { threshold: 0.5 },
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [selector, eventName]);
}

/**
 * Track when an element is visible for a sustained duration (dwell time).
 */
function useTrackDwell(selector: string, eventName: string, dwellMs: number) {
  useEffect(() => {
    const el = document.querySelector(selector);
    if (!el) return;
    let timer: ReturnType<typeof setTimeout> | null = null;
    let fired = false;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (fired) return;
        if (entry.isIntersecting) {
          timer = setTimeout(() => {
            track(eventName);
            fired = true;
            observer.disconnect();
          }, dwellMs);
        } else if (timer) {
          clearTimeout(timer);
          timer = null;
        }
      },
      { threshold: 0.5 },
    );
    observer.observe(el);
    return () => {
      if (timer) clearTimeout(timer);
      observer.disconnect();
    };
  }, [selector, eventName, dwellMs]);
}

export function HomepageTracker() {
  const interactedRef = useRef(false);

  // ── Section visibility (fixed: was broken due to ref race condition) ──
  useTrackVisible('[data-track="try_form"]', 'homepage_section_viewed_try_form');
  useTrackVisible('[data-track="how_it_works"]', 'homepage_section_viewed_how_it_works');
  useTrackVisible('[data-track="cta"]', 'homepage_section_viewed_cta');

  // ── Scenario dwell: visible for 3+ continuous seconds ──
  useTrackDwell('[data-track="try_form"]', 'homepage_scenario_viewed', 3000);

  // ── Click tracking (CTA + link) via data attributes ──
  const handleCtaClick = useCallback((button: string) => {
    track('homepage_cta_clicked', { button });
  }, []);

  const handleLinkClick = useCallback((link: string) => {
    track('homepage_link_clicked', { link });
  }, []);

  useEffect(() => {
    const handleClick = (e: Event) => {
      interactedRef.current = true;
      const target = (e.target as HTMLElement).closest('[data-track-click]');
      if (!target) return;
      const action = target.getAttribute('data-track-click');
      const type = target.getAttribute('data-track-type') || 'cta';
      if (action) {
        if (type === 'link') {
          handleLinkClick(action);
        } else {
          handleCtaClick(action);
        }
      }
    };
    document.addEventListener('click', handleClick);
    return () => document.removeEventListener('click', handleClick);
  }, [handleCtaClick, handleLinkClick]);

  // ── homepage_loaded: baseline denominator ──
  useEffect(() => {
    track('homepage_loaded', {
      viewport_height: window.innerHeight,
      device: getDeviceCategory(),
      referrer_host: document.referrer ? new URL(document.referrer).hostname : 'direct',
    });
  }, []);

  // ── homepage_engaged: stayed 5+ seconds ──
  useEffect(() => {
    const timer = setTimeout(() => track('homepage_engaged'), 5000);
    return () => clearTimeout(timer);
  }, []);

  // ── homepage_inactive_bounce: 30s with zero interactions ──
  useEffect(() => {
    const markInteracted = () => { interactedRef.current = true; };
    const events = ['click', 'scroll', 'touchstart', 'keydown'] as const;
    events.forEach((e) => document.addEventListener(e, markInteracted, { once: true, passive: true }));

    const timer = setTimeout(() => {
      if (!interactedRef.current) {
        track('homepage_inactive_bounce');
      }
    }, 30000);

    return () => {
      clearTimeout(timer);
      events.forEach((e) => document.removeEventListener(e, markInteracted));
    };
  }, []);

  // ── homepage_scroll_depth: 25/50/75/100% milestones ──
  useEffect(() => {
    const milestones = new Set([25, 50, 75, 100]);
    const fired = new Set<number>();

    const handleScroll = () => {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      if (docHeight <= 0) return;
      const pct = Math.round((scrollTop / docHeight) * 100);

      for (const m of milestones) {
        if (pct >= m && !fired.has(m)) {
          fired.add(m);
          track('homepage_scroll_depth', { depth: m });
          milestones.delete(m);
        }
      }
      if (milestones.size === 0) {
        window.removeEventListener('scroll', handleScroll);
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return null;
}
