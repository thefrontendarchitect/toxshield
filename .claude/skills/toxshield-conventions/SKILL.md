---
name: toxshield-conventions
description: ToxShield coding conventions, patterns, and architecture decisions. Use when writing code, creating components, or making architectural decisions.
user-invocable: false
---

# ToxShield Project Conventions

**Full reference:** Root `CLAUDE.md` and `AGENTS.md`.

## Architecture

- **Single Next.js 16 app** — NOT a monorepo
- App Router with route groups: `(app)/` (protected), `(auth)/` (public auth)
- API routes in `src/app/api/`
- Components organized by domain: `analysis/`, `dashboard/`, `layout/`, `ui/`

## Key Imports

```typescript
// Supabase (server-side)
import { createClient } from '@/lib/supabase/server';
// Supabase (client-side)
import { createClient } from '@/lib/supabase/client';
// AI engine
import { analyzePersonality } from '@/lib/ai/engine';
// Types
import type { AnalysisResult } from '@/types/analysis';
import type { PersonRow, AnalysisRow } from '@/types/database';
// Validation
import { z } from 'zod';
```

## Key Rules (Quick Reference)

1. **Design Tokens**: Use surface-*, neon-cyan, neon-magenta, neon-mint, arcane-glass, etc. NEVER raw hex values. See [../../../AGENTS.md](../../../AGENTS.md).
2. **Page Layout**: AppHeader (top) + BottomNav (bottom) + AuroraBackground + main content. See [page-patterns.md](page-patterns.md).
3. **API Routes**: Zod validation + Supabase auth check + business logic + NextResponse.json. See [api-patterns.md](api-patterns.md).
4. **Typography**: Standard Tailwind CSS 4 sizes. Inter (body) + JetBrains Mono (UI/terminal) + Anton (display). See [typography.md](typography.md).
5. **Forms**: React Hook Form + Zod resolver
6. **AI Output**: Claude tool_use for structured JSON, validated with Zod schemas
7. **Dark Theme Only**: Never use bg-white, light grays, or light-mode colors
8. **Type Safety**: Always use `.returns<Type>()` on Supabase queries
