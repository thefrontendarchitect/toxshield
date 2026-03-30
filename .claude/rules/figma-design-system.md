# Figma Design System Rules — ToxShield

> **Machine-readable rules** for converting Figma designs to code.
> Auto-loaded by agents from `.claude/rules/`. Source of truth for Figma-to-code translation.

---

## Rule 1: Color Variable Mapping

When you see a Figma color, convert it to the ToxShield Arcane token:

| Figma Color / Description | Tailwind Class | Example |
|--------------------------|----------------|---------|
| Deep blue-black background (~#080519) | `surface-0` | `bg-surface-0` |
| Dark blue panel (~#0f0b28) | `surface-1` | `bg-surface-1` |
| Elevated blue surface (~#181340) | `surface-2` | `bg-surface-2` |
| Purple border/divider (~#241e55) | `surface-3` | `border-surface-3` |
| Interactive hover (~#12102e) | `hover` | `bg-hover` |
| Subtle line/divider (~#1a1538) | `line` | `border-line` |
| Bright cyan (~#00b4ff) | `neon-cyan` | `text-neon-cyan`, `bg-neon-cyan` |
| Bright magenta/pink (~#ff2878) | `neon-magenta` | `text-neon-magenta`, `bg-neon-magenta` |
| Bright mint green (~#50ffa0) | `neon-mint` | `text-neon-mint`, `bg-neon-mint` |
| Gold/amber (~#ffc832) | `warning-amber` | `text-warning-amber` |
| Purple glow (~#dc3cff) | `critical-magenta` | `text-critical-magenta` |
| Bright blue-white text (~#f0f6ff) | `text-primary` | `text-text-primary` |
| Soft blue muted text (~#b8d4f0) | `text-secondary` | `text-text-secondary` |
| Dimmed text/icon (~#7a9bc0) | `dim` | `text-dim` |
| Very muted (~#3a4f6a) | `muted` | `text-muted` |
| Magenta badge/status (~#ff2878) | `badge-pink` | `text-badge-pink` |

**Semantic aliases** (same underlying values):
- `toxic-green` = `neon-mint` (#50ffa0)
- `danger-red` = `neon-magenta` (#ff2878)
- `safe-blue` = `neon-cyan` (#00b4ff)

**NEVER use raw hex or rgb values.** Always convert to token classes.

---

## Rule 2: Typography Conversion

ToxShield uses **standard Tailwind CSS 4 typography** plus custom fonts:

| Figma Font | Tailwind Class | Notes |
|-----------|----------------|-------|
| 10px Mono Bold Uppercase | `font-mono text-[10px] font-bold uppercase tracking-[0.1em]` | Badges, nav labels |
| 11px Mono Medium Uppercase | `font-mono text-[11px] font-medium uppercase tracking-[0.2em]` | Section labels (or `label-section` class) |
| 12px Regular | `text-xs` | Small labels |
| 14px Regular | `text-sm` | Secondary text |
| 14px Medium | `text-sm font-medium` | Medium labels |
| 16px Regular | `text-base` | Body text (default) |
| 16px Medium | `text-base font-medium` | Card titles |
| 18px Medium | `text-lg font-medium` | Section headings |
| 20px Medium | `text-xl font-medium` | Page headings |
| 24px Bold | `text-2xl font-bold` | Large headings |
| 44px+ Bold Uppercase | `hero-title` class or `font-display text-4xl+ uppercase` | Hero/landing text |

**Fonts:**
- Body text: `font-sans` (Inter) — default, no class needed
- Terminal/UI elements: `font-mono` (JetBrains Mono)
- Display/hero headings: `font-display` (Anton)

---

## Rule 3: Shadow, Glow & Glass Conversion

ToxShield uses Arcane glow and glassmorphism classes:

| Figma Effect | CSS Class | Notes |
|-------------|-----------|-------|
| Cyan glow/highlight | `glow` | Box-shadow with neon-cyan (3-layer) |
| Subtle cyan glow | `glow-subtle` | Soft box-shadow for nav/subtle elements |
| Intense cyan glow | `glow-intense` | Strong 3-layer glow for hero elements |
| Magenta/pink glow | `glow-magenta` | Box-shadow with neon-magenta |
| Mint/green glow | `glow-mint` | Box-shadow with neon-mint |
| Cyan text glow | `text-glow` | Text-shadow for emphasis |
| Subtle text glow | `text-glow-subtle` | Soft text-shadow for nav labels |
| Magenta text glow | `text-glow-magenta` | Text-shadow for danger |
| Mint text glow | `text-glow-mint` | Text-shadow for success |
| Frosted glass panel | `arcane-glass` | 80% bg, 8px blur, border, rounded-lg |
| Strong frosted glass | `arcane-glass-intense` | 88% bg, 12px blur, 2px border, rounded-xl |
| Dossier card | `card-dashed` | 75% bg, 16px blur, dashed border |
| Scanline overlay | `scanlines` | Hextech energy lines (add `relative` to parent) |

---

## Rule 4: Component Identification

When implementing a Figma screen, identify these ToxShield components:

### Layout
- **Fixed top bar with glass effect** -> `AppHeader` (`src/components/layout/app-header.tsx`)
- **Fixed bottom nav with icons** -> `BottomNav` (`src/components/layout/bottom-nav.tsx`)
- **Animated aurora gradient background** -> `AuroraBackground` (`src/components/ui/aurora-background.tsx`)

### Analysis Results
- **Circular score visualization** -> `ToxicityRing` — toxicity score ring (0-10)
- **Color-coded risk pill** -> `RiskBadge` — low (cyan), moderate (amber), high (magenta)
- **List of traits with severity** -> `TraitList` — detected toxic traits
- **Main result card** -> `ThreatProfile` — full analysis display
- **2-3 sentence summary** -> `PatternAnalysis` — behavioral pattern text
- **3 action items** -> `ProtectionStrategies` — protection strategy cards
- **Reflection feedback** -> `SelfReflectionCard` — only when NOT toxic

### Dashboard
- **Statistics cards** -> `StatsGrid` — total people, high-risk, analyses count
- **Health percentage** -> `EnvironmentHealth` — aggregate environment score
- **Trend chart** -> `HealthTrend` — health score over time
- **Achievement badges** -> `BadgeShelf` — earned badges

### UI Primitives
- **Text input with bottom border** -> `FormInput` (`src/components/ui/form-input.tsx`)
- **Frosted glass card with tape** -> `PolaroidCard` (`src/components/ui/polaroid-card.tsx`)
- **Status indicator pill** -> `StatusBadge` (`src/components/ui/status-badge.tsx`)
- **SVG progress ring** -> `AnimatedRing` (`src/components/ui/animated-ring.tsx`)
- **Custom navigation icons** -> `DossierIcons` (`src/components/ui/dossier-icons.tsx`)

---

## Rule 5: Spacing Patterns

### Page Layout
```
AppHeader (fixed top, arcane-glass, min-h-[56px], pt-safe)
  main content (bg-surface-0/60, grid-bg, pt-[72px], pb-[100px], min-h-screen)
    content wrapper (px-4, py-6)
BottomNav (fixed bottom, arcane-glass, h-16, pb-safe)
```

### Common Spacing
| Pattern | Tailwind |
|---------|----------|
| Main content padding | `px-4 py-6` |
| Card padding | `p-4` to `p-5` |
| Section gap | `space-y-6` |
| List item gap | `space-y-4` |
| Inline element gap | `gap-2` to `gap-3` |

### Mobile Touch Targets
| Pattern | Tailwind |
|---------|----------|
| Minimum button size | `min-h-[44px] min-w-[44px]` |
| Nav item minimum | `min-h-[44px] min-w-[56px]` |
| Form input minimum | `min-h-[48px]` |

---

## Rule 6: Element Type Decision Tree

```
Is it a score display?
  YES -> ToxicityRing component (circular, 0-10 scale, neon-cyan)

Is it a risk level indicator?
  YES -> RiskBadge component
         Low: bg-safe-blue/10 text-safe-blue (cyan)
         Moderate: bg-warning-amber/10 text-warning-amber
         High: bg-danger-red/10 text-danger-red (magenta)

Is it a card/panel?
  YES -> arcane-glass class (or card-dashed for dossier-style)
         Add border-neon-cyan/[0.06] for subtle border

Is it a form input?
  YES -> bg-transparent border-b border-neon-cyan/15 text-text-primary
         focus:border-neon-cyan/40 transition-colors min-h-[48px]
         Label: font-mono text-[10px] uppercase tracking-[0.2em] text-neon-cyan/70

Is it a primary button?
  YES -> bg-neon-cyan text-surface-0 font-mono rounded-md
         hover:bg-neon-cyan/90 min-h-[44px]

Is it a danger button?
  YES -> bg-neon-magenta text-white rounded-md min-h-[44px]

Is it a section label?
  YES -> Use label-section class (or font-mono text-[11px] uppercase tracking-[0.2em] text-neon-cyan/70)

Is it a status badge?
  YES -> Use badge-status class (magenta) or tag-badge class (cyan)
```

---

## Rule 7: Icon Conventions

ToxShield uses **custom SVG dossier-icons** for navigation (`src/components/ui/dossier-icons.tsx`):

| Context | Icon Component | Active Color |
|---------|---------------|-------------|
| Dashboard nav | `FingerprintIcon` | `text-surface-0` on `bg-neon-cyan glow-subtle` |
| Analysis | `BrainIcon` | Same |
| People/Evidence | `EyeIcon` | Same |
| Pulse | `PulseIcon` | Same |
| Header folder | `FolderIcon` | `text-neon-cyan/40` |

Active nav state: Icon gets `bg-neon-cyan glow-subtle` background with `text-surface-0` icon color.
Inactive nav state: `text-neon-cyan/30` icon color.
Nav labels: `font-mono text-[10px] uppercase tracking-[0.15em]`, active: `text-neon-cyan font-bold text-glow-subtle`.

For other contexts, use `lucide-react` icons with Arcane-appropriate colors (neon-cyan, dim, text-secondary).

---

## Rule 8: Common Figma-to-Code Pitfalls

1. **Figma uses light backgrounds** — ToxShield is dark-mode only, convert to surface-* tokens (deep blue-purple, NOT gray)
2. **Figma shows standard shadows** — Convert to `glow-*` or `arcane-glass` classes (dark themes use glow, not drop-shadow)
3. **Figma uses absolute positioning** — Convert to flex/grid layouts
4. **Figma uses decorative fonts** — Stick to Inter (body) + JetBrains Mono (UI/terminal) + Anton (display/hero)
5. **Figma shows colored backgrounds on badges** — Use `bg-{color}/10 text-{color}` pattern, or `badge-status`/`tag-badge` classes
6. **Never use bg-white or gray-*** — Use `arcane-glass` or `bg-surface-1`/`bg-surface-2` instead
7. **Never use old glow classes** — `glow-green` is now `glow`, `glow-red` is now `glow-magenta`, `glow-amber` is removed
8. **Cards must use glassmorphism** — Use `arcane-glass` or `card-dashed`, not plain `bg-surface-1 border border-surface-3`
9. **Touch targets must be 44px+** — All interactive elements need `min-h-[44px]`
10. **Borders use low-opacity neon** — `border-neon-cyan/[0.06]` to `border-neon-cyan/[0.08]`, not solid `border-surface-3`

---

## Quick Reference Card

```
SURFACES:  surface-0 (#080519)   surface-1 (#0f0b28)
           surface-2 (#181340)   surface-3 (#241e55)
           hover (#12102e)       line (#1a1538)

NEONS:     neon-cyan (#00b4ff)   neon-magenta (#ff2878)
           neon-mint (#50ffa0)   warning-amber (#ffc832)
           critical-magenta (#dc3cff)

TEXT:      text-primary (#f0f6ff)   text-secondary (#b8d4f0)
           dim (#7a9bc0)            muted (#3a4f6a)

GLOWS:     glow / glow-subtle / glow-intense (cyan box-shadow)
           glow-magenta / glow-mint (colored box-shadow)
           text-glow / text-glow-subtle / text-glow-intense (cyan text-shadow)
           text-glow-magenta / text-glow-mint (colored text-shadow)

GLASS:     arcane-glass (standard cards)
           arcane-glass-intense (modals/hero)
           card-dashed (dossier cards)

UTILS:     badge-status (magenta)   label-section (cyan)
           tag-badge (cyan dashed)  hero-title (display heading)
           grid-bg (hextech grid)   arcane-particles (floating)

LAYOUT:    AppHeader (fixed top) + BottomNav (fixed bottom)
           AuroraBackground + grid-bg
           main: pt-[72px] pb-[100px] px-4 py-6
```
