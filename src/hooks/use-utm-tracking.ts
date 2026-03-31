'use client';

import { useEffect } from 'react';
import { track } from '@vercel/analytics';

/**
 * Reads UTM params from the URL on mount and fires custom Vercel Analytics
 * events. Bridges Instagram's Referer-stripping and Vercel free tier's
 * inability to parse UTM parameters.
 */
export function useUtmTracking() {
  useEffect(() => {
    const key = 'utm_tracked';
    if (sessionStorage.getItem(key)) return;

    const params = new URLSearchParams(window.location.search);
    const utmSource = params.get('utm_source');
    if (!utmSource) return;

    const utmMedium = params.get('utm_medium');
    const utmContent = params.get('utm_content');
    const utmCampaign = params.get('utm_campaign');

    track('utm_visit', {
      source: utmSource,
      ...(utmMedium && { medium: utmMedium }),
      ...(utmContent && { content: utmContent }),
      ...(utmCampaign && { campaign: utmCampaign }),
    });

    if (utmSource === 'ig' || utmSource === 'instagram') {
      track('instagram_visit', {
        medium: utmMedium ?? 'unknown',
        content: utmContent ?? 'unknown',
      });
    }

    sessionStorage.setItem(key, '1');
  }, []);
}
