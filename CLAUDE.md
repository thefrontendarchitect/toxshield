@AGENTS.md

## Conventions
- Use Tailwind CSS 4 Arcane theme tokens (surface-0, neon-cyan, neon-magenta, neon-mint, arcane-glass, etc.) — never raw hex values
- All API routes: validate with Zod, check Supabase auth, return NextResponse.json
- Database queries use Supabase client with `.returns<Type>()` for type safety
- AI structured output uses Claude tool_use + Zod schema validation
- Components go in `src/components/{category}/` — analysis/, dashboard/, layout/, ui/
- Types go in `src/types/` — keep analysis types, database types, and entity types separate
- Server-side Supabase: `import { createClient } from '@/lib/supabase/server'`
- Client-side Supabase: `import { createClient } from '@/lib/supabase/client'`
