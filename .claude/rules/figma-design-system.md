# Figma Design System Rules — ToxShield

> **Machine-readable rules** for converting Figma designs to code.
> Auto-loaded by agents from `.claude/rules/`. Source of truth for Figma-to-code translation.

---

## Rule 1: Color Variable Mapping

When you see a Figma color, convert it to the ToxShield token:

| Figma Color / Description | Tailwind Class | Example |
|--------------------------|----------------|---------|
| Near-black background (~#0a0a0a) | `surface-0` | `bg-surface-0` |
| Dark panel/sidebar (~#141414) | `surface-1` | `bg-surface-1` |
| Elevated surface (~#1e1e1e) | `surface-2` | `bg-surface-2` |
| Border/divider (~#282828) | `surface-3` | `border-surface-3` |
| Neon green (~#00ff41) | `toxic-green` | `text-toxic-green`, `bg-toxic-green` |
| Dim green (~#2d6b3a) | `toxic-green-dim` | `text-toxic-green-dim` |
| Red/danger (~#e53e3e) | `danger-red` | `text-danger-red`, `bg-danger-red` |
| Amber/warning (~#d69e2e) | `warning-amber` | `text-warning-amber` |
| Blue/safe (~#4299e1) | `safe-blue` | `text-safe-blue` |
| Magenta/critical (~#d53f8c) | `critical-magenta` | `text-critical-magenta` |
| Light text (~#e8e8e8) | `text-primary` | `text-text-primary` |
| Muted text (~#6b6b6b) | `text-secondary` | `text-text-secondary` |
| Green text (terminal) | `text-terminal` | `text-text-terminal` |

**NEVER use raw hex or oklch values.** Always convert to token classes.

---

## Rule 2: Typography Conversion

ToxShield uses **standard Tailwind CSS 4 typography** (no custom overrides):

| Figma Font | Tailwind Class | Notes |
|-----------|----------------|-------|
| 12px Regular | `text-xs` | Small labels, badges |
| 14px Regular | `text-sm` | Secondary text, sidebar nav |
| 14px Medium | `text-sm font-medium` | Medium labels |
| 16px Regular | `text-base` | Body text (default) |
| 16px Medium | `text-base font-medium` | Card titles |
| 18px Medium | `text-lg font-medium` | Section headings |
| 20px Medium | `text-xl font-medium` | Page headings |
| 24px Bold | `text-2xl font-bold` | Hero text |

**Fonts:**
- Body text: `font-sans` (Inter) — default, no class needed
- Terminal/code elements: `font-mono` (JetBrains Mono)

---

## Rule 3: Shadow & Glow Conversion

ToxShield uses CSS glow classes instead of traditional shadows:

| Figma Effect | CSS Class | Notes |
|-------------|-----------|-------|
| Green glow/highlight | `glow-green` | Box-shadow with toxic-green |
| Red glow/danger | `glow-red` | Box-shadow with danger-red |
| Amber glow/warning | `glow-amber` | Box-shadow with warning-amber |
| Green text glow | `text-glow-green` | Text-shadow for emphasis |
| Red text glow | `text-glow-red` | Text-shadow for danger |
| Scanline overlay | `scanlines` | CRT-style lines (add `relative` to parent) |

---

## Rule 4: Component Identification

When implementing a Figma screen, identify these ToxShield components:

### Layout
- **Top bar with red/amber/green dots** -> `TerminalHeader` (`src/components/layout/terminal-header.tsx`)
- **Left nav with monospace links** -> `Sidebar` (`src/components/layout/sidebar.tsx`)

### Analysis Results
- **Circular score visualization** -> `ToxicityRing` — toxicity score ring (0-10)
- **Color-coded risk pill** -> `RiskBadge` — low (blue), moderate (amber), high (red)
- **List of traits with severity** -> `TraitList` — detected toxic traits
- **Main result card** -> `ThreatProfile` — full analysis display
- **2-3 sentence summary** -> `PatternAnalysis` — behavioral pattern text
- **3 action items** -> `ProtectionStrategies` — protection strategy cards
- **Reflection feedback** -> `SelfReflectionCard` — only when NOT toxic

### Dashboard
- **Statistics cards** -> `StatsGrid` — total people, high-risk, analyses count
- **Health percentage** -> `EnvironmentHealth` — aggregate environment score

---

## Rule 5: Spacing Patterns

### Page Layout
```
TerminalHeader (fixed top)
Sidebar (fixed left, w-56)
  main content (flex-1, overflow-y-auto, p-6)
```

### Common Spacing
| Pattern | Tailwind |
|---------|----------|
| Main content padding | `p-6` |
| Card padding | `p-4` to `p-6` |
| Section gap | `space-y-6` |
| List item gap | `space-y-4` |
| Inline element gap | `gap-2` to `gap-3` |

---

## Rule 6: Element Type Decision Tree

```
Is it a score display?
  YES -> ToxicityRing component (circular, 0-10 scale)

Is it a risk level indicator?
  YES -> RiskBadge component
         Low: bg-safe-blue/10 text-safe-blue
         Moderate: bg-warning-amber/10 text-warning-amber
         High: bg-danger-red/10 text-danger-red

Is it a dark card/panel?
  YES -> bg-surface-1 border border-surface-3 rounded-lg

Is it a form input?
  YES -> bg-surface-1 border border-surface-3 rounded-md text-text-primary
         focus:border-toxic-green focus:ring-toxic-green/20

Is it a primary button?
  YES -> bg-toxic-green text-surface-0 font-mono rounded-md
         hover:bg-toxic-green/90

Is it a danger button?
  YES -> bg-danger-red text-white rounded-md
```

---

## Rule 7: Icon Conventions

ToxShield uses **monospace ASCII characters** for navigation icons in the sidebar:

| Context | Icon | Color |
|---------|------|-------|
| Dashboard nav | `>` | `text-text-secondary` (active: `text-toxic-green`) |
| New Analysis | `+` | Same |
| People list | `#` | Same |
| Settings | `*` | Same |
| Sign out | `<` | `text-text-secondary` (hover: `text-danger-red`) |

For other contexts, use `lucide-react` icons with terminal-appropriate colors.

---

## Rule 8: Common Figma-to-Code Pitfalls

1. **Figma uses light backgrounds** — ToxShield is dark-mode only, convert to surface-* tokens
2. **Figma shows standard shadows** — Convert to glow-* classes or remove (dark themes rarely need shadows)
3. **Figma uses absolute positioning** — Convert to flex/grid layouts
4. **Figma uses decorative fonts** — Stick to Inter (body) + JetBrains Mono (terminal elements)
5. **Figma shows colored backgrounds on badges** — Use `bg-{color}/10 text-{color}` pattern for subtle badges on dark bg
6. **Never use bg-white** — Use `bg-surface-1` or `bg-surface-2` instead

---

## Quick Reference Card

```
COLORS:    surface-0 = bg (#0a0a0a)    surface-1 = panels (#141414)
           surface-2 = elevated         surface-3 = borders
           toxic-green = accent         danger-red = high risk
           warning-amber = moderate     safe-blue = low risk

TEXT:      text-primary = content       text-secondary = muted
           text-terminal = green        font-mono = terminal elements

GLOWS:     glow-green / glow-red / glow-amber (box-shadow)
           text-glow-green / text-glow-red (text-shadow)
           scanlines (CRT overlay)       cursor-blink (terminal cursor)

LAYOUT:    TerminalHeader + Sidebar + main (p-6)
           bg-surface-1 border-surface-3 rounded-lg (cards)
           space-y-6 (sections)          space-y-4 (lists)
```
