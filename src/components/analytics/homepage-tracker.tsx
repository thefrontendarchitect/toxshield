'use client';

import { useEffect, useRef, useCallback } from 'react';
import { track } from '@vercel/analytics';

function useTrackVisible(ref: React.RefObject<HTMLElement | null>, eventName: string) {
  useEffect(() => {
    const el = ref.current;
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
  }, [eventName]);
}

export function HomepageTracker() {
  const tryFormRef = useRef<HTMLDivElement>(null);
  const howItWorksRef = useRef<HTMLDivElement>(null);
  const ctaRef = useRef<HTMLDivElement>(null);

  useTrackVisible(tryFormRef, 'homepage_section_viewed_try_form');
  useTrackVisible(howItWorksRef, 'homepage_section_viewed_how_it_works');
  useTrackVisible(ctaRef, 'homepage_section_viewed_cta');

  const handleCtaClick = useCallback((button: string) => {
    track('homepage_cta_clicked', { button });
  }, []);

  const handleLinkClick = useCallback((link: string) => {
    track('homepage_link_clicked', { link });
  }, []);

  // Attach observers to sections via data attributes after mount
  useEffect(() => {
    const attach = (attr: string, ref: React.RefObject<HTMLElement | null>) => {
      const el = document.querySelector(`[data-track="${attr}"]`);
      if (el) (ref as React.MutableRefObject<HTMLElement | null>).current = el as HTMLElement;
    };
    attach('try_form', tryFormRef);
    attach('how_it_works', howItWorksRef);
    attach('cta', ctaRef);
  }, []);

  // Attach click handlers to tracked elements
  useEffect(() => {
    const handleClick = (e: Event) => {
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

  return null;
}
