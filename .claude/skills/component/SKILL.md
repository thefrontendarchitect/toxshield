---
name: component
description: Create a new React component in ToxShield's component library. Use when adding reusable UI components.
argument-hint: [ComponentName] [category]
disable-model-invocation: true
allowed-tools: Write, Read, Edit, Glob, Grep
---

# Create Component

Create a new React component in the ToxShield `src/components/` directory.

## Arguments

- `$0` - Component name in PascalCase (e.g., `RiskTimeline`, `InputCard`)
- `$1` - Category: `analysis`, `dashboard`, `layout`, `input`, `share`, or `ui`

## Component Location

```
src/components/$1/
└── $0.tsx              # Component implementation (kebab-case filename)
```

## Implementation Steps

### 1. Create Component File

```tsx
'use client';

interface $0Props {
  className?: string;
  // Add component-specific props
}

export function $0({ className }: $0Props) {
  return (
    <div className={`${className ?? ''}`}>
      {/* Component content */}
    </div>
  );
}
```

### 2. Follow Arcane Theme

All components MUST use ToxShield's Arcane dark theme:

```tsx
// Card component example
<div className="arcane-glass p-4">
  <h3 className="font-mono text-sm text-neon-cyan">{title}</h3>
  <p className="text-text-secondary mt-1">{description}</p>
</div>
```

### 3. Risk-Level Color Pattern

```tsx
const riskColors = {
  low: 'text-safe-blue bg-safe-blue/10',
  moderate: 'text-warning-amber bg-warning-amber/10',
  high: 'text-danger-red bg-danger-red/10',
} as const;
```

### 4. Glow Effect Pattern

```tsx
// For highlighted/active elements
<div className="arcane-glass glow border border-neon-cyan/20 p-4">
  {/* Glowing card content */}
</div>

// For neon text emphasis
<span className="text-neon-cyan text-glow font-mono">
  {score}
</span>

// For danger emphasis
<span className="text-neon-magenta text-glow-magenta font-mono">
  {dangerScore}
</span>
```

## Component Categories

| Category | Purpose | Examples |
|----------|---------|---------|
| `analysis` | Analysis result display | ToxicityRing, RiskBadge, TraitList, ThreatProfile |
| `dashboard` | Dashboard-specific | StatsGrid, EnvironmentHealth, HealthTrend, BadgeShelf |
| `layout` | App chrome | AppHeader, BottomNav, PageContainer |
| `people` | People/subject views | PersonHeader, PersonList, ShareCard |
| `insights` | User insights | InsightsSummary, InsightsTimeline |
| `ui` | Reusable primitives | FormInput, StatusBadge, PolaroidCard, AuroraBackground, DossierIcons, AnimatedRing, Spinner, ErrorAlert |

## Design Token Reference

```
SURFACES:  bg-surface-0 (page) / arcane-glass (cards) / bg-surface-2 (hover)
BORDERS:   border-neon-cyan/[0.06] to border-neon-cyan/[0.08]
NEONS:     text-neon-cyan / text-neon-magenta / text-neon-mint / text-warning-amber
TEXT:      text-text-primary / text-text-secondary / text-dim / text-muted
FONTS:     font-mono (UI elements) / font-display (hero) / default (body)
GLOWS:     glow / glow-subtle / glow-magenta / glow-mint
           text-glow / text-glow-subtle / text-glow-magenta / text-glow-mint
GLASS:     arcane-glass / arcane-glass-intense / card-dashed
EFFECTS:   scanlines / cursor-blink / score-pulse / touch-active / touch-ripple
```

## Checklist

- [ ] Uses Arcane theme tokens (no bg-white, no light colors, no raw hex)
- [ ] Props interface defined and typed
- [ ] `'use client'` directive if using hooks/state/events
- [ ] Mobile-first (touch targets min 44px, responsive)
- [ ] `font-mono` used for UI/label elements
- [ ] Cards use `arcane-glass` or `card-dashed` for glassmorphism
- [ ] Glow effects use `glow` / `text-glow` classes (not old glow-green)
