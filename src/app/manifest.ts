import type { MetadataRoute } from 'next';

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'ToxShield — Forensic Relationship Analyzer',
    short_name: 'ToxShield',
    description:
      'AI-powered behavioral analysis. Log a person, get a threat profile.',
    start_url: '/',
    display: 'standalone',
    background_color: '#080519',
    theme_color: '#00b4ff',
    icons: [
      { src: '/favicon.ico', sizes: 'any', type: 'image/x-icon' },
      { src: '/apple-icon.png', sizes: '180x180', type: 'image/png' },
    ],
  };
}
