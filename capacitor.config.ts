import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.toxshield.app',
  appName: 'ToxShield',
  webDir: 'out',

  server: {
    // Point to deployed ToxShield web app
    // For local dev: use your machine's IP (not localhost — Android can't reach it)
    // For production: replace with your deployed URL
    url: process.env.CAPACITOR_SERVER_URL || 'https://www.toxshield.in/',
    androidScheme: 'https',
    cleartext: false,
  },

  plugins: {
    SplashScreen: {
      launchShowDuration: 0,
      launchAutoHide: false,
      backgroundColor: '#000000',
      androidScaleType: 'CENTER_CROP',
      showSpinner: false,
      splashFullScreen: true,
      splashImmersive: true,
    },
    Keyboard: {
      resize: 'native',
      style: 'DARK',
      resizeOnFullScreen: false,
    },
    StatusBar: {
      style: 'DARK',
      backgroundColor: '#000000',
    },
  },

  android: {
    allowMixedContent: false,
    appendUserAgent: 'ToxShieldApp/1.0',
    buildOptions: {
      keystorePath: 'android/app/release.keystore',
    },
  },
};

export default config;
