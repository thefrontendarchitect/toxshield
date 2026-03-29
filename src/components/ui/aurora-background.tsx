'use client';

import { useMemo } from 'react';

/**
 * Arcane Aurora Background — full 5-layer composition.
 *
 * Layers (bottom to top):
 * 1. Aurora blobs — blurred radial gradients
 * 2. Splatter glow — soft neon accent blobs
 * 3. GRAFFITI DOODLES — SVG neon doodles (skulls, X-marks, lightning, etc.)
 * 4. Energy particles — CSS floating streaks
 */

// ── Seeded RNG (deterministic per session) ──────────────────────────
function seededRng(seed: number) {
  let s = seed;
  return () => {
    s = (s * 1664525 + 1013904223) & 0xffffffff;
    return (s >>> 0) / 0xffffffff;
  };
}

// ── Neon colors (Hextech Core palette) ──────────────────────────────
const NEON = [
  'rgba(0,180,255,',   // cyan
  'rgba(255,40,120,',  // magenta
  'rgba(80,255,160,',  // mint
];

// ── SVG Doodle Generators ───────────────────────────────────────────
// Each returns an SVG string fragment positioned at (0,0), caller wraps in <g transform>

function doodleXMark(s: number, opacity: number, color: string): string {
  const sz = 12 + s * 20;
  return `<line x1="${-sz}" y1="${-sz}" x2="${sz}" y2="${sz}" stroke="${color}${opacity})" stroke-width="3" stroke-linecap="round"/>
<line x1="${sz}" y1="${-sz}" x2="${-sz}" y2="${sz}" stroke="${color}${opacity})" stroke-width="3" stroke-linecap="round"/>`;
}

function doodleLightning(s: number, opacity: number, color: string): string {
  const h = 40 + s * 60;
  const seg = 4 + Math.floor(s * 3);
  const segH = h / seg;
  let d = `M 0 0`;
  let cx = 0;
  for (let i = 1; i <= seg; i++) {
    cx += (((i * 7 + s * 100) % 30) - 15);
    d += ` L ${cx} ${i * segH}`;
  }
  return `<path d="${d}" fill="none" stroke="${color}${opacity})" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>`;
}

function doodleSkull(s: number, opacity: number, color: string): string {
  const r = 18 + s * 14;
  const c = `${color}${opacity})`;
  // Head circle
  let svg = `<circle cx="0" cy="0" r="${r}" fill="none" stroke="${c}" stroke-width="2.5"/>`;
  // Spikes from top
  const spikes = 5 + Math.floor(s * 4);
  for (let i = 0; i < spikes; i++) {
    const angle = -Math.PI + (Math.PI / spikes) * i + (Math.PI / (spikes * 2));
    const len = r * (0.5 + s * 0.3);
    const x1 = Math.cos(angle) * r;
    const y1 = Math.sin(angle) * r;
    const x2 = Math.cos(angle) * (r + len);
    const y2 = Math.sin(angle) * (r + len);
    svg += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${c}" stroke-width="2"/>`;
  }
  // X eyes
  const eyeOff = r * 0.35;
  const eyeS = r * 0.18;
  for (const dx of [-1, 1]) {
    const ex = dx * eyeOff;
    const ey = -r * 0.1;
    svg += `<line x1="${ex - eyeS}" y1="${ey - eyeS}" x2="${ex + eyeS}" y2="${ey + eyeS}" stroke="${c}" stroke-width="2"/>`;
    svg += `<line x1="${ex + eyeS}" y1="${ey - eyeS}" x2="${ex - eyeS}" y2="${ey + eyeS}" stroke="${c}" stroke-width="2"/>`;
  }
  // Teeth grid
  const mouthY = r * 0.35;
  const mouthW = r * 0.5;
  svg += `<line x1="${-mouthW}" y1="${mouthY}" x2="${mouthW}" y2="${mouthY}" stroke="${c}" stroke-width="2"/>`;
  for (let i = 0; i < 4; i++) {
    const tx = -mouthW + (mouthW * 2 / 3) * i;
    svg += `<line x1="${tx}" y1="${mouthY - 4}" x2="${tx}" y2="${mouthY + 4}" stroke="${c}" stroke-width="1.5"/>`;
  }
  return svg;
}

function doodleSmiley(s: number, opacity: number, color: string): string {
  const r = 16 + s * 16;
  const c = `${color}${opacity})`;
  let svg = `<circle cx="0" cy="0" r="${r}" fill="none" stroke="${c}" stroke-width="2.5"/>`;
  // X eyes
  const eyeS = r * 0.15;
  for (const dx of [-1, 1]) {
    const ex = dx * r * 0.3;
    const ey = -r * 0.15;
    svg += `<line x1="${ex - eyeS}" y1="${ey - eyeS}" x2="${ex + eyeS}" y2="${ey + eyeS}" stroke="${c}" stroke-width="2"/>`;
    svg += `<line x1="${ex + eyeS}" y1="${ey - eyeS}" x2="${ex - eyeS}" y2="${ey + eyeS}" stroke="${c}" stroke-width="2"/>`;
  }
  // Stitched smile
  const smW = r * 0.45;
  const smY = r * 0.25;
  svg += `<path d="M ${-smW} ${smY} Q 0 ${smY + r * 0.35} ${smW} ${smY}" fill="none" stroke="${c}" stroke-width="2"/>`;
  return svg;
}

function doodleExplosionStar(s: number, opacity: number, color: string): string {
  const rays = 6 + Math.floor(s * 6);
  const outerR = 20 + s * 30;
  const innerR = outerR * 0.4;
  let points = '';
  for (let i = 0; i < rays * 2; i++) {
    const angle = (Math.PI / rays) * i;
    const r = i % 2 === 0 ? outerR : innerR;
    points += `${Math.cos(angle) * r},${Math.sin(angle) * r} `;
  }
  return `<polygon points="${points.trim()}" fill="none" stroke="${color}${opacity})" stroke-width="2"/>`;
}

function doodleArrow(s: number, opacity: number, color: string): string {
  const len = 35 + s * 45;
  const angle = s * Math.PI * 2;
  const x2 = Math.cos(angle) * len;
  const y2 = Math.sin(angle) * len;
  const headLen = 14;
  const c = `${color}${opacity})`;
  let svg = `<line x1="0" y1="0" x2="${x2}" y2="${y2}" stroke="${c}" stroke-width="3" stroke-linecap="round"/>`;
  for (const da of [0.5, -0.5]) {
    const hx = x2 - Math.cos(angle + da) * headLen;
    const hy = y2 - Math.sin(angle + da) * headLen;
    svg += `<line x1="${x2}" y1="${y2}" x2="${hx}" y2="${hy}" stroke="${c}" stroke-width="3" stroke-linecap="round"/>`;
  }
  return svg;
}

function doodleRune(s: number, opacity: number, color: string): string {
  const r = 14 + s * 22;
  const c = `${color}${opacity})`;
  const ic = `${color}${opacity * 0.5})`;
  let svg = `<circle cx="0" cy="0" r="${r}" fill="none" stroke="${c}" stroke-width="2"/>`;
  const ir = r * 0.6;
  const pattern = Math.floor(s * 4);
  if (pattern === 0) {
    svg += `<line x1="${-ir}" y1="0" x2="${ir}" y2="0" stroke="${ic}" stroke-width="1.5"/>`;
    svg += `<line x1="0" y1="${-ir}" x2="0" y2="${ir}" stroke="${ic}" stroke-width="1.5"/>`;
  } else if (pattern === 1) {
    const pts = [0, 1, 2].map(i => {
      const a = (i * Math.PI * 2 / 3) - Math.PI / 2;
      return `${Math.cos(a) * ir},${Math.sin(a) * ir}`;
    }).join(' ');
    svg += `<polygon points="${pts}" fill="none" stroke="${ic}" stroke-width="1.5"/>`;
  } else if (pattern === 2) {
    svg += `<circle cx="0" cy="0" r="${ir}" fill="none" stroke="${ic}" stroke-width="1.5"/>`;
    svg += `<circle cx="0" cy="0" r="3" fill="${c}"/>`;
  } else {
    svg += `<line x1="${-ir}" y1="${-ir}" x2="${ir}" y2="${ir}" stroke="${ic}" stroke-width="1.5"/>`;
    svg += `<line x1="${ir}" y1="${-ir}" x2="${-ir}" y2="${ir}" stroke="${ic}" stroke-width="1.5"/>`;
  }
  return svg;
}

function doodleBomb(s: number, opacity: number, color: string): string {
  const r = 14 + s * 16;
  const c = `${color}${opacity})`;
  let svg = `<circle cx="0" cy="0" r="${r}" fill="none" stroke="${c}" stroke-width="2.5"/>`;
  // Fuse
  const fuseLen = r * 0.8;
  svg += `<line x1="${r - 3}" y1="${-r + 3}" x2="${r + fuseLen * 0.5}" y2="${-r - fuseLen}" stroke="${c}" stroke-width="2"/>`;
  // Spark
  const sx = r + fuseLen * 0.5;
  const sy = -r - fuseLen;
  const sp = 5;
  svg += `<line x1="${sx - sp}" y1="${sy}" x2="${sx + sp}" y2="${sy}" stroke="${c}" stroke-width="1.5"/>`;
  svg += `<line x1="${sx}" y1="${sy - sp}" x2="${sx}" y2="${sy + sp}" stroke="${c}" stroke-width="1.5"/>`;
  return svg;
}

function doodleGear(s: number, opacity: number, color: string): string {
  const r = 16 + s * 20;
  const teeth = [6, 8, 10][Math.floor(s * 3)];
  const toothLen = r * 0.35;
  const c = `${color}${opacity})`;
  let svg = `<circle cx="0" cy="0" r="${r}" fill="none" stroke="${c}" stroke-width="2"/>`;
  for (let i = 0; i < teeth; i++) {
    const angle = (Math.PI * 2 / teeth) * i;
    const x1 = Math.cos(angle) * r;
    const y1 = Math.sin(angle) * r;
    const x2 = Math.cos(angle) * (r + toothLen);
    const y2 = Math.sin(angle) * (r + toothLen);
    svg += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${c}" stroke-width="3"/>`;
  }
  svg += `<circle cx="0" cy="0" r="3.5" fill="${c}"/>`;
  return svg;
}

function doodleHexCrystal(s: number, opacity: number, color: string): string {
  const h = 20 + s * 30;
  const w = h * 0.45;
  const c = `${color}${opacity})`;
  const ic = `${color}${opacity * 0.5})`;
  const points = `0,${-h} ${w},${-h / 2} ${w},${h / 2} 0,${h} ${-w},${h / 2} ${-w},${-h / 2}`;
  return `<polygon points="${points}" fill="none" stroke="${c}" stroke-width="2"/>
<line x1="0" y1="${-h + 3}" x2="0" y2="${h - 3}" stroke="${ic}" stroke-width="1.5"/>`;
}

function doodleGraffitiText(s: number, opacity: number, color: string): string {
  const words = ['TOXIC!', 'BOOM', 'LIAR', 'RUN', 'FAKE', 'DENY', 'TRAP', 'NAH', 'HA HA'];
  const word = words[Math.floor(s * words.length)];
  const size = 16 + s * 14;
  const c = `${color}${opacity})`;
  // Stroke outline for graffiti look
  return `<text x="0" y="0" font-family="Impact,Arial Black,sans-serif" font-size="${size}" fill="${c}" text-anchor="middle" dominant-baseline="central" stroke="${color}${opacity * 0.3})" stroke-width="2" paint-order="stroke">${word}</text>`;
}

function doodleDrip(s: number, opacity: number, color: string): string {
  const len = 30 + s * 80;
  const c = `${color}${opacity})`;
  let d = 'M 0 0';
  for (let i = 1; i <= 8; i++) {
    const x = ((i * 7 + s * 50) % 6) - 3;
    d += ` L ${x} ${(len / 8) * i}`;
  }
  // Bulb at end
  return `<path d="${d}" fill="none" stroke="${c}" stroke-width="2" stroke-linecap="round"/>
<circle cx="0" cy="${len}" r="3" fill="${c}"/>`;
}

function doodleSmallStar(s: number, opacity: number, color: string): string {
  const sz = 6 + s * 10;
  const inner = sz * 0.3;
  let points = '';
  for (let i = 0; i < 8; i++) {
    const a = (Math.PI / 4) * i - Math.PI / 2;
    const r = i % 2 === 0 ? sz : inner;
    points += `${Math.cos(a) * r},${Math.sin(a) * r} `;
  }
  const c = `${color}${opacity})`;
  return s > 0.5
    ? `<polygon points="${points.trim()}" fill="${c}"/>`
    : `<polygon points="${points.trim()}" fill="none" stroke="${c}" stroke-width="1.5"/>`;
}

function doodleScribbleCircle(s: number, opacity: number, color: string): string {
  const r = 14 + s * 24;
  const c = `${color}${opacity})`;
  let svg = '';
  const passes = 2 + Math.floor(s * 2);
  for (let p = 0; p < passes; p++) {
    const dx = ((p * 13 + s * 100) % 8) - 4;
    const dy = ((p * 7 + s * 70) % 8) - 4;
    svg += `<circle cx="${dx}" cy="${dy}" r="${r}" fill="none" stroke="${c}" stroke-width="2"/>`;
  }
  return svg;
}

function doodleHeart(s: number, opacity: number, color: string): string {
  const sz = 12 + s * 14;
  const c = `${color}${opacity})`;
  return `<path d="M 0 ${sz * 0.4} C ${-sz * 0.5} ${-sz * 0.3} ${-sz} ${-sz * 0.6} 0 ${-sz * 0.15} C ${sz} ${-sz * 0.6} ${sz * 0.5} ${-sz * 0.3} 0 ${sz * 0.4} Z" fill="none" stroke="${c}" stroke-width="2"/>`;
}

function doodleCrosshair(s: number, opacity: number, color: string): string {
  const r = 14 + s * 18;
  const c = `${color}${opacity})`;
  const ext = r * 1.2;
  return `<circle cx="0" cy="0" r="${r}" fill="none" stroke="${c}" stroke-width="2"/>
<line x1="${-ext}" y1="0" x2="${ext}" y2="0" stroke="${c}" stroke-width="1.5"/>
<line x1="0" y1="${-ext}" x2="0" y2="${ext}" stroke="${c}" stroke-width="1.5"/>
<circle cx="0" cy="0" r="2.5" fill="${c}"/>`;
}

// ── Weighted doodle list (matches Python weights) ───────────────────
const DOODLE_FUNCS = [
  doodleSkull, doodleSkull,
  doodleSmiley, doodleSmiley,
  doodleXMark, doodleXMark, doodleXMark,
  doodleGraffitiText, doodleGraffitiText, doodleGraffitiText,
  doodleLightning, doodleLightning,
  doodleArrow, doodleArrow,
  doodleExplosionStar,
  doodleRune,
  doodleBomb,
  doodleGear,
  doodleHexCrystal,
  doodleDrip, doodleDrip,
  doodleSmallStar, doodleSmallStar, doodleSmallStar,
  doodleScribbleCircle,
  doodleHeart,
  doodleCrosshair,
];

// ── Generate doodle placements ──────────────────────────────────────
interface DoodlePlacement {
  x: number;
  y: number;
  scale: number;
  rotation: number;
  svg: string;
}

function generateDoodles(count: number, seed: number): DoodlePlacement[] {
  const rng = seededRng(seed);
  const doodles: DoodlePlacement[] = [];

  for (let i = 0; i < count; i++) {
    const x = rng() * 100;     // % position
    const y = rng() * 100;

    // 70% chance to skip center zone (preserve text readability)
    const inCenter = x > 25 && x < 75 && y > 30 && y < 70;
    if (inCenter && rng() < 0.7) continue;

    const scale = 0.72 + rng() * 1.01; // 0.72x–1.73x — 20% more
    const rotation = rng() * 360;
    const opacity = 0.5 + rng() * 0.4; // 50-90% opacity — bright neon pop
    const colorIdx = Math.floor(rng() * NEON.length);
    const funcIdx = Math.floor(rng() * DOODLE_FUNCS.length);
    const s = rng(); // shape variation seed

    const svg = DOODLE_FUNCS[funcIdx](s, opacity, NEON[colorIdx]);

    doodles.push({ x, y, scale, rotation, svg });
  }

  return doodles;
}

// ── Simple string hash ──────────────────────────────────────────────
export function hashString(str: string): number {
  let hash = 5381;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) + hash + str.charCodeAt(i)) & 0xffffffff;
  }
  return hash >>> 0;
}

// ── Component ───────────────────────────────────────────────────────
export function AuroraBackground({ seed }: { seed?: number }) {
  const doodles = useMemo(() => generateDoodles(80, seed ?? 42069), [seed]);

  return (
    <div
      className="pointer-events-none fixed inset-0 -z-10 overflow-hidden"
      aria-hidden="true"
    >
      {/* Layer 1: Aurora blobs */}
      <div
        className="absolute top-[15%] left-[15%] h-[50vh] w-[50vh] rounded-full opacity-40"
        style={{
          background: 'radial-gradient(circle, rgba(0,140,255,0.4) 0%, transparent 70%)',
          filter: 'blur(80px)',
        }}
      />
      <div
        className="absolute top-[30%] right-[15%] h-[40vh] w-[40vh] rounded-full opacity-35"
        style={{
          background: 'radial-gradient(circle, rgba(120,40,200,0.35) 0%, transparent 70%)',
          filter: 'blur(70px)',
        }}
      />
      <div
        className="absolute bottom-[20%] left-[50%] h-[45vh] w-[45vh] -translate-x-1/2 rounded-full opacity-35"
        style={{
          background: 'radial-gradient(circle, rgba(0,100,220,0.4) 0%, transparent 70%)',
          filter: 'blur(75px)',
        }}
      />
      <div
        className="absolute bottom-[30%] left-[20%] h-[35vh] w-[35vh] rounded-full opacity-30"
        style={{
          background: 'radial-gradient(circle, rgba(80,0,180,0.3) 0%, transparent 70%)',
          filter: 'blur(60px)',
        }}
      />

      {/* Layer 2: Splatter glow */}
      <div
        className="absolute top-[10%] right-[30%] h-[20vh] w-[20vh] rounded-full opacity-20"
        style={{
          background: 'radial-gradient(circle, rgba(0,180,255,0.5) 0%, transparent 70%)',
          filter: 'blur(40px)',
        }}
      />
      <div
        className="absolute bottom-[15%] right-[20%] h-[18vh] w-[18vh] rounded-full opacity-15"
        style={{
          background: 'radial-gradient(circle, rgba(255,40,120,0.4) 0%, transparent 70%)',
          filter: 'blur(35px)',
        }}
      />
      <div
        className="absolute top-[60%] left-[10%] h-[15vh] w-[15vh] rounded-full opacity-18"
        style={{
          background: 'radial-gradient(circle, rgba(80,255,160,0.4) 0%, transparent 70%)',
          filter: 'blur(30px)',
        }}
      />

      {/* Layer 3: GRAFFITI DOODLES — the soul of Arcane */}
      <svg
        className="absolute inset-0 w-full h-full"
        viewBox="0 0 1080 2400"
        preserveAspectRatio="xMidYMid slice"
        xmlns="http://www.w3.org/2000/svg"
      >
        {doodles.map((d, i) => (
          <g
            key={i}
            transform={`translate(${d.x * 10.8}, ${d.y * 24}) scale(${d.scale}) rotate(${d.rotation})`}
            dangerouslySetInnerHTML={{ __html: d.svg }}
          />
        ))}
      </svg>

      {/* Layer 4: Energy particles */}
      <div className="arcane-particles absolute inset-0" />
    </div>
  );
}
