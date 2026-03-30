# Typography Reference

**Authoritative source:** `src/app/globals.css` and `src/app/layout.tsx`.

## Fonts

| Font | CSS Variable | Tailwind Class | Usage |
|------|-------------|----------------|-------|
| Inter | `--font-inter` | default (`font-sans`) | Body text, headings, forms |
| JetBrains Mono | `--font-jetbrains-mono` | `font-mono` | UI labels, badges, nav, scores, terminal elements |
| Anton | `--font-anton` | `font-display` | Hero/display headings, landing page titles |

## Standard Tailwind CSS 4 Sizes

ToxShield uses **standard** Tailwind CSS 4 typography (no custom overrides):

| Class | Size | Usage |
|-------|------|-------|
| `text-[10px]` | 10px | Badges, nav labels, form labels (with font-mono) |
| `text-[11px]` | 11px | Section labels (label-section class) |
| `text-xs` | 12px | Small labels, terminal chrome |
| `text-sm` | 14px | Secondary text, nav items |
| `text-base` | 16px | Default body text |
| `text-lg` | 18px | Section headings |
| `text-xl` | 20px | Page titles |
| `text-2xl` | 24px | Large headings |
| `text-4xl`+ | 36px+ | Hero/display text (with font-display) |

## Weight Classes

| Class | Weight | Usage |
|-------|--------|-------|
| `font-normal` | 400 | Body text |
| `font-medium` | 500 | Card titles, labels |
| `font-semibold` | 600 | Section headings |
| `font-bold` | 700 | Logo, major headings, badges |
| `font-black` | 900 | Hero titles (hero-title class) |

## Arcane UI Typography Patterns

Elements with the Arcane UI feel should use:
- `font-mono` — JetBrains Mono for all UI elements
- `text-neon-cyan` — primary neon accent color
- `text-glow` or `text-glow-subtle` — cyan text glow effect
- `tracking-[0.1em]` to `tracking-[0.2em]` — letter spacing for labels
- `uppercase` — for labels like "CASE_FILE_0821"

### Common Patterns
- **Form labels**: `font-mono text-[10px] uppercase tracking-[0.2em] text-neon-cyan/70` (or `label-section` class)
- **Nav labels**: `font-mono text-[10px] uppercase tracking-[0.15em]`
- **Status badges**: `font-mono text-[10px] font-bold uppercase tracking-[0.1em]` (or `badge-status` class)
- **Section headers**: `label-section` class (font-mono, 11px, uppercase, tracking-wide, cyan)
- **Hero/display**: `hero-title` class or `font-display text-4xl+ font-black uppercase`
