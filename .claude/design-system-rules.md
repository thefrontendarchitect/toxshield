# ToxShield Design System Rules

## 1. Token Definitions

### Where Tokens Are Defined
- **Tailwind CSS 4 Theme**: `src/app/globals.css` — `@theme inline` block with OKLch color variables
- **Fonts**: `src/app/layout.tsx` — Inter (sans) + JetBrains Mono (mono) via next/font/google

### Color System (OKLch-based dark terminal palette)

| Token | OKLch Value | Approx Hex | Usage |
|---|---|---|---|
| `surface-0` | `oklch(0.1 0.01 260)` | ~#0a0a0a | Page background |
| `surface-1` | `oklch(0.14 0.01 260)` | ~#141414 | Sidebar, header, cards |
| `surface-2` | `oklch(0.18 0.01 260)` | ~#1e1e1e | Hover states, elevated surfaces |
| `surface-3` | `oklch(0.22 0.01 260)` | ~#282828 | Borders, dividers, scrollbar |
| `toxic-green` | `oklch(0.85 0.2 145)` | ~#00ff41 | Primary accent, active states, glow |
| `toxic-green-dim` | `oklch(0.45 0.12 145)` | ~#2d6b3a | Subtle green highlights |
| `danger-red` | `oklch(0.65 0.25 25)` | ~#e53e3e | High risk, errors, danger |
| `warning-amber` | `oklch(0.75 0.18 75)` | ~#d69e2e | Moderate risk, warnings |
| `safe-blue` | `oklch(0.7 0.15 230)` | ~#4299e1 | Low risk, info states |
| `critical-magenta` | `oklch(0.6 0.25 330)` | ~#d53f8c | Critical severity accent |
| `text-primary` | `oklch(0.92 0.01 260)` | ~#e8e8e8 | Primary text |
| `text-secondary` | `oklch(0.55 0.01 260)` | ~#6b6b6b | Secondary/muted text |
| `text-terminal` | `oklch(0.85 0.2 145)` | ~#00ff41 | Terminal-style green text |

**Risk level color mapping:**
- Low risk: `safe-blue`
- Moderate risk: `warning-amber`
- High risk: `danger-red`
- Critical severity: `critical-magenta`

**NEVER use raw oklch/hex values.** Always use token classes (e.g., `bg-surface-1`, `text-toxic-green`).

### Typography

| Context | Font | Tailwind Class | Notes |
|---|---|---|---|
| Body text | Inter | default (font-sans) | Primary readable font |
| Code/terminal/monospace | JetBrains Mono | `font-mono` | Sidebar labels, header, scores |
| Heading | Inter | `text-lg font-bold` to `text-2xl font-bold` | Standard Tailwind sizes |

**Font families:**
- `font-sans` = Inter (set via `--font-inter` CSS variable)
- `font-mono` = JetBrains Mono (set via `--font-jetbrains-mono` CSS variable)

**Tailwind CSS 4 uses STANDARD sizes** (text-xs=12px, text-sm=14px, text-base=16px, etc.). No custom overrides.

### Glow Effects (defined in globals.css)

| CSS Class | Effect | Usage |
|---|---|---|
| `glow-green` | Green box-shadow glow | Highlighted cards, active elements |
| `glow-red` | Red box-shadow glow | Danger indicators |
| `glow-amber` | Amber box-shadow glow | Warning indicators |
| `text-glow-green` | Green text-shadow | Emphasized terminal text, logo |
| `text-glow-red` | Red text-shadow | Danger text emphasis |

### Special Effects

| CSS Class | Effect |
|---|---|
| `scanlines` | CRT scanline overlay (via ::after pseudo-element) |
| `cursor-blink` | Terminal cursor blinking animation |
| `score-pulse` | Pulsing opacity animation for scores |

## 2. Component Library

**No shared component library.** All components are in `src/components/`:

### Analysis Components (`src/components/analysis/`)
- `ToxicityRing` — Circular ring visualization of toxicity score (0-10)
- `RiskBadge` — Color-coded pill showing risk level (low/moderate/high)
- `TraitList` — List of detected toxic traits with severity indicators
- `ThreatProfile` — Main analysis result card layout
- `PatternAnalysis` — Behavioral pattern summary text
- `ProtectionStrategies` — 3 actionable protection strategies
- `SelfReflectionCard` — Shown when person is NOT toxic (self-reflection feedback)

### Dashboard Components (`src/components/dashboard/`)
- `StatsGrid` — Dashboard statistics cards (total people, high-risk, total analyses)
- `EnvironmentHealth` — Overall toxicity environment health percentage

### Layout Components (`src/components/layout/`)
- `Sidebar` — Left navigation with terminal-style links
- `TerminalHeader` — Top bar with red/amber/green dots and terminal path display

### Planned Directories (empty)
- `src/components/input/` — Form input components
- `src/components/share/` — Profile sharing components
- `src/components/ui/` — Reusable UI primitives

## 3. Page Layout Pattern

```tsx
// src/app/(app)/layout.tsx — ALL protected pages use this
<div className="flex flex-col h-screen">
  <TerminalHeader />
  <div className="flex flex-1 overflow-hidden">
    <Sidebar />
    <main className="flex-1 overflow-y-auto p-6">{children}</main>
  </div>
</div>
```

## 4. Color Usage Quick Reference

```
SURFACES:  surface-0 = page bg          surface-1 = sidebar/header/cards
           surface-2 = hover/elevated    surface-3 = borders/dividers

ACCENTS:   toxic-green = primary accent  danger-red = high risk/error
           warning-amber = moderate       safe-blue = low risk/info
           critical-magenta = critical

TEXT:      text-primary = main content   text-secondary = muted/labels
           text-terminal = green accents

GLOWS:     glow-green = box glow         text-glow-green = text glow
           glow-red = danger glow        glow-amber = warning glow
```
