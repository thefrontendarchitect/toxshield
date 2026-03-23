# Typography Reference

**Authoritative source:** `src/app/globals.css` and `src/app/layout.tsx`.

## Fonts

| Font | CSS Variable | Tailwind Class | Usage |
|------|-------------|----------------|-------|
| Inter | `--font-inter` | default (`font-sans`) | Body text, headings, forms |
| JetBrains Mono | `--font-jetbrains-mono` | `font-mono` | Sidebar, header, scores, terminal elements |

## Standard Tailwind CSS 4 Sizes

ToxShield uses **standard** Tailwind CSS 4 typography (no custom overrides):

| Class | Size | Usage |
|-------|------|-------|
| `text-xs` | 12px | Small labels, badges, terminal chrome |
| `text-sm` | 14px | Secondary text, sidebar nav items |
| `text-base` | 16px | Default body text |
| `text-lg` | 18px | Section headings |
| `text-xl` | 20px | Page titles |
| `text-2xl` | 24px | Hero text, major headings |

## Weight Classes

| Class | Weight | Usage |
|-------|--------|-------|
| `font-normal` | 400 | Body text |
| `font-medium` | 500 | Card titles, labels |
| `font-semibold` | 600 | Section headings |
| `font-bold` | 700 | Logo, major headings |

## Terminal Aesthetic

Elements with a "terminal" feel should use:
- `font-mono` — JetBrains Mono
- `text-toxic-green` — neon green color
- `text-glow-green` — green text glow effect
- `tracking-wider` — letter spacing for headings
- `uppercase` — for labels like "BEHAVIORAL THREAT ANALYSIS"
