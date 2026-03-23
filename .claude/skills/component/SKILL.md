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

### 2. Follow Dark Theme

All components MUST use ToxShield's dark terminal theme:

```tsx
// Card component example
<div className="bg-surface-1 border border-surface-3 rounded-lg p-4">
  <h3 className="font-mono text-sm text-toxic-green">{title}</h3>
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
<div className="glow-green border border-toxic-green/30 rounded-lg p-4">
  {/* Glowing card content */}
</div>

// For terminal-style text emphasis
<span className="text-toxic-green text-glow-green font-mono">
  {score}
</span>
```

## Component Categories

| Category | Purpose | Examples |
|----------|---------|---------|
| `analysis` | Analysis result display | ToxicityRing, RiskBadge, TraitList |
| `dashboard` | Dashboard-specific | StatsGrid, EnvironmentHealth |
| `layout` | App chrome | Sidebar, TerminalHeader |
| `input` | Form inputs | (planned) |
| `share` | Sharing features | (planned) |
| `ui` | Reusable primitives | (planned) |

## Design Token Reference

```
SURFACES:  bg-surface-0 (page) / bg-surface-1 (cards) / bg-surface-2 (hover)
BORDERS:   border-surface-3
ACCENTS:   text-toxic-green / text-danger-red / text-warning-amber / text-safe-blue
TEXT:      text-text-primary / text-text-secondary
FONTS:     font-mono (terminal elements) / default (body)
GLOWS:     glow-green / glow-red / text-glow-green
EFFECTS:   scanlines / cursor-blink / score-pulse
```

## Checklist

- [ ] Uses dark theme tokens (no bg-white, no light colors)
- [ ] Props interface defined and typed
- [ ] `'use client'` directive if using hooks/state/events
- [ ] Responsive (works at all widths within the main content area)
- [ ] `font-mono` used for terminal-style elements
- [ ] Glow effects used appropriately for accent elements
