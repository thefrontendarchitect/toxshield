import { ImageResponse } from 'next/og';

export const runtime = 'edge';
export const alt = 'ToxShield — Forensic Relationship Analyzer';
export const size = { width: 1200, height: 630 };
export const contentType = 'image/png';

export default function TwitterImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(145deg, #080519 0%, #0f0b28 40%, #181340 70%, #080519 100%)',
          fontFamily: 'system-ui, -apple-system, sans-serif',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Grid overlay */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            backgroundImage:
              'linear-gradient(rgba(0,180,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,180,255,0.03) 1px, transparent 1px)',
            backgroundSize: '40px 40px',
          }}
        />

        {/* Glow circle */}
        <div
          style={{
            position: 'absolute',
            width: 400,
            height: 400,
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(0,180,255,0.15) 0%, transparent 70%)',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
          }}
        />

        {/* Top label */}
        <div
          style={{
            display: 'flex',
            fontSize: 14,
            color: '#ff2878',
            letterSpacing: '0.3em',
            textTransform: 'uppercase',
            marginBottom: 24,
          }}
        >
          // threat_detection_system
        </div>

        {/* Title */}
        <div
          style={{
            display: 'flex',
            fontSize: 80,
            fontWeight: 900,
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
          }}
        >
          <span style={{ color: '#f0f6ff' }}>TOX</span>
          <span style={{ color: '#00b4ff' }}>SHIELD</span>
        </div>

        {/* Divider + subtitle */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 16,
            marginTop: 20,
          }}
        >
          <div style={{ width: 60, height: 1, background: 'rgba(0,180,255,0.4)' }} />
          <div
            style={{
              fontSize: 14,
              color: '#00b4ff',
              letterSpacing: '0.2em',
              textTransform: 'uppercase',
            }}
          >
            Forensic Behavioral Analysis
          </div>
          <div style={{ width: 60, height: 1, background: 'rgba(0,180,255,0.4)' }} />
        </div>

        {/* Tagline */}
        <div
          style={{
            display: 'flex',
            fontSize: 22,
            color: '#b8d4f0',
            marginTop: 32,
            maxWidth: 600,
            textAlign: 'center',
            lineHeight: 1.5,
          }}
        >
          Know who&apos;s toxic before they know you know.
        </div>

        {/* Bottom stats */}
        <div
          style={{
            display: 'flex',
            gap: 48,
            marginTop: 48,
            alignItems: 'center',
          }}
        >
          {[
            { value: '40+', label: 'Toxic Traits' },
            { value: 'AI', label: 'Powered' },
            { value: '100%', label: 'Private' },
          ].map((stat) => (
            <div
              key={stat.label}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 4,
              }}
            >
              <div style={{ fontSize: 28, fontWeight: 900, color: '#f0f6ff' }}>
                {stat.value}
              </div>
              <div
                style={{
                  fontSize: 10,
                  color: '#7a9bc0',
                  letterSpacing: '0.15em',
                  textTransform: 'uppercase',
                }}
              >
                {stat.label}
              </div>
            </div>
          ))}
        </div>

        {/* URL */}
        <div
          style={{
            position: 'absolute',
            bottom: 28,
            fontSize: 14,
            color: '#3a4f6a',
            letterSpacing: '0.1em',
          }}
        >
          toxshield.in
        </div>
      </div>
    ),
    { ...size }
  );
}
