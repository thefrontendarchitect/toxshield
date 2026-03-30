---
name: new-feature
description: Create a new feature module with components, types, and API integration. Use when adding a new feature to ToxShield.
argument-hint: [feature-name]
disable-model-invocation: true
allowed-tools: Write, Read, Glob, Grep
---

# Create New Feature

Create a complete feature module for ToxShield.

## Arguments

- `$0` - Feature name (kebab-case, e.g., `chat-analysis`, `export-report`)

## Feature Structure

Depending on complexity, create some or all of these:

```
src/
├── app/(app)/$0/
│   └── page.tsx              # Feature page
├── app/api/$0/
│   └── route.ts              # API endpoint (if needed)
├── components/$0/
│   └── (feature components)  # Feature-specific components
├── lib/$0/
│   └── (utilities)           # Feature-specific utilities
└── types/
    └── $0.ts                 # Feature types (or extend existing)
```

## Implementation Steps

### 1. Define Types

Create or extend type definitions in `src/types/`:

```typescript
// src/types/$0.ts
export interface FeatureData {
  id: string;
  // ... feature-specific fields
}
```

### 2. Create API Route (if needed)

```typescript
// src/app/api/$0/route.ts
import { createClient } from '@/lib/supabase/server';
import { NextResponse } from 'next/server';
import { z } from 'zod';

const requestSchema = z.object({
  // Validate request fields
});

export async function POST(request: Request) {
  // Auth + validation + business logic + response
}
```

### 3. Create Components

```typescript
// src/components/$0/feature-card.tsx
'use client';

export function FeatureCard({ data }: { data: FeatureData }) {
  return (
    <div className="arcane-glass p-4">
      {/* Arcane theme component */}
    </div>
  );
}
```

### 4. Create Page

```typescript
// src/app/(app)/$0/page.tsx
export default function FeaturePage() {
  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-text-primary">Feature Title</h1>
      {/* Page content */}
    </div>
  );
}
```

### 5. Add Navigation (if top-level feature)

Update bottom nav in `src/components/layout/bottom-nav.tsx`:
```typescript
const navItems = [
  // ... existing items
  { href: '/$0', label: 'FEATURE', Icon: FeatureIcon },
];
```
Add a new icon in `src/components/ui/dossier-icons.tsx` if needed.

## Templates

- [types.ts template](templates/types.ts.template)
- [api.ts template](templates/api.ts.template)
- [hooks.ts template](templates/hooks.ts.template)
- [query-keys.ts template](templates/query-keys.ts.template)
- [index.ts template](templates/index.ts.template)

## ToxShield Rules

1. **Dark Arcane theme only** — Use surface-*, neon-cyan, neon-magenta, neon-mint tokens; arcane-glass for cards
2. **Arcane aesthetic** — Use font-mono for UI elements, font-display for hero text, glow/text-glow effects
3. **Auth required** — All (app) routes are protected by middleware
4. **Type safety** — Zod validation on inputs, typed Supabase queries
5. **Supabase integration** — Use server/client clients appropriately
6. **Mobile-first** — Touch targets min 44px, use pt-safe/pb-safe for safe areas

## Supabase Migration (if new table needed)

Add to `supabase/migrations/`:
```sql
-- NNN_create_feature_table.sql
CREATE TABLE feature_table (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  -- feature columns
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE feature_table ENABLE ROW LEVEL SECURITY;

-- RLS policy: users can only see their own data
CREATE POLICY "Users can view own data" ON feature_table
  FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own data" ON feature_table
  FOR INSERT WITH CHECK (auth.uid() = user_id);
```

## Example Usage

```
/new-feature chat-analysis
```

Creates the feature structure for WhatsApp chat analysis with page, API route, and components.
