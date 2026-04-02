import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Mobile (Capacitor): static export
  ...(process.env.BUILD_MODE === 'mobile' && {
    output: 'export',
    trailingSlash: true,
  }),

  // Docker: standalone server
  ...(process.env.BUILD_MODE === 'docker' && {
    output: 'standalone',
  }),

  // Dev: no output mode (standard SSR) — default when BUILD_MODE is unset

  images: {
    unoptimized: process.env.BUILD_MODE === 'mobile' || process.env.BUILD_MODE === 'docker',
  },

  async redirects() {
    return [
      {
        source: '/:path*',
        has: [{ type: 'host', value: 'www.toxshield.in' }],
        destination: 'https://toxshield.in/:path*',
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
