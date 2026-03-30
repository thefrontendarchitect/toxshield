# ToxShield Design System Rules

## 1. Token Definitions

### Where Tokens Are Defined
- **Tailwind CSS 4 Theme**: `src/app/globals.css` — `@theme inline` block with CSS variable color tokens
- **Fonts**: `src/app/layout.tsx` — Inter (sans) + JetBrains Mono (mono) + Anton (display) via next/font/google
- **Palettes**: `src/app/globals.css` — 5 palettes via `[data-palette]` attribute

### Color System (Arcane — Hextech Core)

| Token | Hex Value | Usage |
|---|---|---|
| `surface-0` | `#080519` | Page background (deep blue-black aurora) |
| `surface-1` | `#0f0b28` | Elevated panels |
| `surface-2` | `#181340` | Hover states, elevated surfaces |
| `surface-3` | `#241e55` | Borders, dividers |
| `black` | `#080519` | Alias for surface-0 |
| `hover` | `#12102e` | Interactive hover background |
| `line` | `#1a1538` | Subtle divider lines |
| `neon-cyan` | `#00b4ff` | **Primary accent**, active states, glows |
| `neon-magenta` | `#ff2878` | Danger, high risk, status badges |
| `neon-mint` | `#50ffa0` | Success, safe states |
| `toxic-green` | `#50ffa0` | Alias for neon-mint (legacy compat) |
| `danger-red` | `#ff2878` | Alias for neon-magenta — high risk, errors |
| `warning-amber` | `#ffc832` | Moderate risk, warnings |
| `safe-blue` | `#00b4ff` | Alias for neon-cyan — low risk, info |
| `critical-magenta` | `#dc3cff` | Critical severity accent |
| `badge-pink` | `#ff2878` | Status badge accent |
| `badge-pink-bg` | `rgba(255,40,120,0.15)` | Status badge background |
| `text-primary` | `#f0f6ff` | Primary text (bright blue-white) |
| `text-secondary` | `#b8d4f0` | Secondary/muted text (soft blue) |
| `white` | `#f0f6ff` | Alias for text-primary |
| `dim` | `#7a9bc0` | Dimmed text/icons |
| `muted` | `#3a4f6a` | Very muted text/borders |

**Risk level color mapping:**
- Low risk: `safe-blue` / `neon-cyan`
- Moderate risk: `warning-amber`
- High risk: `danger-red` / `neon-magenta`
- Critical severity: `critical-magenta`

**NEVER use raw hex values.** Always use token classes (e.g., `bg-surface-1`, `text-neon-cyan`, `border-neon-magenta/20`).

### Typography

| Context | Font | Tailwind Class | Notes |
|---|---|---|---|
| Body text | Inter | default (`font-sans`) | Primary readable font |
| Code/terminal/monospace | JetBrains Mono | `font-mono` | UI labels, badges, nav, scores |
| Display/hero headings | Anton | `font-display` | Large uppercase titles |
| Heading | Inter | `text-lg font-bold` to `text-2xl font-bold` | Standard Tailwind sizes |

**Font families:**
- `font-sans` = Inter (set via `--font-inter` CSS variable)
- `font-mono` = JetBrains Mono (set via `--font-jetbrains-mono` CSS variable)
- `font-display` = Anton (set via `--font-anton` CSS variable)

**Tailwind CSS 4 uses STANDARD sizes** (text-xs=12px, text-sm=14px, text-base=16px, etc.). No custom overrides.

**Common mono patterns:**
- Labels: `font-mono text-[10px] uppercase tracking-[0.2em] text-neon-cyan/70` (or use `label-section` class)
- Badges: `font-mono text-[10px] font-bold uppercase tracking-[0.1em]`
- Nav items: `font-mono text-[10px] uppercase tracking-[0.15em]`

### Glow Effects (defined in globals.css)

| CSS Class | Effect | Usage |
|---|---|---|
| `glow` | Cyan box-shadow glow (3-layer) | Highlighted cards, active elements |
| `glow-subtle` | Soft cyan box-shadow | Nav active states, subtle emphasis |
| `glow-intense` | Strong cyan glow (3-layer) | Hero elements, major highlights |
| `glow-magenta` | Magenta box-shadow glow | Danger indicators, high-risk elements |
| `glow-mint` | Mint box-shadow glow | Success indicators |
| `text-glow` | Cyan text-shadow | Emphasized text, headings |
| `text-glow-subtle` | Soft cyan text-shadow | Nav labels, subtle text emphasis |
| `text-glow-intense` | Strong cyan text-shadow (3-layer) | Hero text |
| `text-glow-magenta` | Magenta text-shadow | Danger text emphasis |
| `text-glow-mint` | Mint text-shadow | Success text emphasis |

### Glassmorphism (defined in globals.css)

| CSS Class | Effect | Usage |
|---|---|---|
| `arcane-glass` | Frosted glass (80% bg, 8px blur, subtle border, rounded-lg) | Cards, panels, header, nav |
| `arcane-glass-intense` | Stronger glass (88% bg, 12px blur, 2px border, rounded-xl) | Modals, hero cards |
| `card-dashed` | Glass with dashed border (75% bg, 16px blur) | Dossier-style cards |

### Utility Classes (defined in globals.css)

| CSS Class | Effect | Usage |
|---|---|---|
| `badge-status` | Magenta badge (mono, 10px, uppercase, bordered) | Status indicators |
| `label-section` | Cyan section label (mono, 11px, uppercase, tracking-wide) | Section headers |
| `tag-badge` | Cyan tag with dashed border (mono, 10px, uppercase) | Tag/category labels |
| `hero-title` | Display font, 2.75rem, uppercase, cyan text-shadow | Landing/hero headings |
| `grid-bg` | Hextech energy grid overlay (cyan lines, 40px grid) | Page backgrounds |
| `arcane-particles` | Floating energy particles (cyan, magenta, mint) | Background ambiance |

### Special Effects & Animations

| CSS Class | Effect |
|---|---|
| `scanlines` | Hextech energy line overlay (via ::after pseudo-element) |
| `cursor-blink` | Terminal cursor blinking animation |
| `score-pulse` | Pulsing opacity animation for scores (2s) |
| `line-pulse` | Pulsing border opacity (3s) |
| `border-flash` | Flashing border color animation (2s) |
| `touch-active` | Scale-down on press (0.98, 100ms) |
| `touch-ripple` | Radial cyan ripple on touch |

### 5-Palette System

Palettes switch via `data-palette` attribute on root HTML element:

| Palette | Data Attribute | Mood |
|---|---|---|
| Hextech Core | (default) | Blue-purple aurora, cyan/magenta/mint neons |
| Jinx's Chaos | `data-palette="jinx"` | Deep magenta base, cooler neons |
| Zaun Undercity | `data-palette="zaun"` | Green-tinted dark, mint-dominant |
| Piltover Gold | `data-palette="piltover"` | Gold/bronze tones, gold accents |
| Shimmer | `data-palette="shimmer"` | Purple-pink base, magenta-focused |

All palettes override the same CSS variables, so components are automatically re-themed.

## 2. Component Library

All components are in `src/components/`:

### Analysis Components (`src/components/analysis/`)
- `ToxicityRing` — Circular ring visualization of toxicity score (0-10)
- `RiskBadge` — Color-coded pill showing risk level (low/moderate/high)
- `TraitList` — List of detected toxic traits with severity indicators
- `ThreatProfile` — Main analysis result card layout
- `PatternAnalysis` — Behavioral pattern summary text
- `ProtectionStrategies` — 3 actionable protection strategies
- `SelfReflectionCard` — Shown when person is NOT toxic
- `UserInsightCard` — User's own behavioral insight
- `TextModeForm` / `ChatModeForm` / `SlackModeForm` / `QuickModeForm` — Analysis input forms

### Dashboard Components (`src/components/dashboard/`)
- `StatsGrid` — Dashboard statistics cards
- `EnvironmentHealth` — Overall toxicity environment health percentage
- `HealthTrend` — Health score trend visualization
- `StreakCounter` — Analysis streak display
- `BadgeShelf` — Achievement badges display

### Layout Components (`src/components/layout/`)
- `AppHeader` — Fixed top bar with arcane-glass, dossier icon, title (replaces TerminalHeader)
- `BottomNav` — Fixed bottom navigation with dossier-icons, neon-cyan active states
- `PageContainer` — Content wrapper
- `Sidebar` — Legacy left navigation (not used in current mobile layout)
- `TerminalHeader` — Legacy top bar (not used in current mobile layout)

### People Components (`src/components/people/`)
- `PersonHeader` — Person detail header
- `PersonList` — List of tracked subjects
- `ShareCard` — Shareable profile card

### Insights Components (`src/components/insights/`)
- `InsightsSummary` — User insights overview
- `InsightsTimeline` — Timeline of insights

### UI Components (`src/components/ui/`)
- `FormInput` / `FormTextarea` / `FormSelect` — Styled form inputs (border-b, neon-cyan focus)
- `StatusBadge` — Variant badges (critical/warning/stable/default)
- `PolaroidCard` — Card with arcane-glass, tape effect, status badges
- `AuroraBackground` — 5-layer animated aurora gradient with graffiti doodles
- `AnimatedRing` — SVG progress ring with neon-cyan
- `DossierIcons` — Custom SVG icons (FingerprintIcon, BrainIcon, EyeIcon, PulseIcon, FolderIcon, etc.)
- `Spinner` — Loading spinner
- `ErrorAlert` — Cyan error alert
- `PaywallModal` — Premium feature modal
- `PersonMatchBanner` — Person match notification
- `NotificationPrompt` — Push notification prompt
- `GoogleIcon` — Google OAuth icon

## 3. Page Layout Pattern

```tsx
// src/app/(app)/layout.tsx — ALL protected pages use this
<>
  <AuroraBackground seed={hashString(pathname)} />
  <AppHeader title={title} showBackButton={isDetailPage} />
  <main className="bg-surface-0/60 grid-bg pt-[72px] pb-[100px] min-h-screen relative">
    <div className="px-4 py-6">{children}</div>
  </main>
  <BottomNav />
</>
```

**Mobile-first patterns:**
- `pt-safe` / `pb-safe` — Respect device safe areas (notch, home indicator)
- Touch targets: min `min-h-[44px]` / `min-w-[56px]`
- Form inputs: `min-h-[48px]`
- Borders: Use low-opacity neon (`border-neon-cyan/[0.06]` to `border-neon-cyan/[0.08]`)

## 4. Color Usage Quick Reference

```
SURFACES:  surface-0 = page bg (#080519)    surface-1 = panels (#0f0b28)
           surface-2 = elevated (#181340)    surface-3 = borders (#241e55)
           hover = interactive (#12102e)     line = dividers (#1a1538)

NEONS:     neon-cyan = primary (#00b4ff)     neon-magenta = danger (#ff2878)
           neon-mint = success (#50ffa0)     warning-amber = warning (#ffc832)
           critical-magenta = critical (#dc3cff)

TEXT:      text-primary = content (#f0f6ff)  text-secondary = muted (#b8d4f0)
           dim = dimmed (#7a9bc0)            muted = very dim (#3a4f6a)

GLOWS:     glow / glow-subtle / glow-intense (box-shadow, cyan)
           glow-magenta / glow-mint (box-shadow, colored)
           text-glow / text-glow-subtle / text-glow-intense (text-shadow)
           text-glow-magenta / text-glow-mint (text-shadow, colored)

GLASS:     arcane-glass (standard) / arcane-glass-intense (modals)
           card-dashed (dossier cards)

LAYOUT:    AppHeader (fixed top) + BottomNav (fixed bottom) + AuroraBackground
           main: pt-[72px] pb-[100px] px-4 py-6
           arcane-glass + border-neon-cyan/[0.06] (cards)
```
