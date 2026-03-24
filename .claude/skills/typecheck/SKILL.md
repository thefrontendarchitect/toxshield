---
name: typecheck
description: Run TypeScript type checking and fix any errors found.
disable-model-invocation: true
allowed-tools: Bash(pnpm *), Read, Edit, Glob, Grep
---

# TypeScript Type Check

Run TypeScript type checking for ToxShield and fix any errors.

## Command

```bash
npx tsc --noEmit
```

## Error Resolution Workflow

### 1. Run Type Check
Run `npx tsc --noEmit` and collect all errors.

### 2. Categorize Errors
Group errors by type:
- **Missing types**: Need to add type definitions
- **Type mismatches**: Wrong type assignments
- **Import errors**: Missing exports or wrong paths
- **Null/undefined**: Need null checks or optional chaining

### 3. Fix Priority
1. Type definition files first (`src/types/`)
2. Lib/utility files (`src/lib/`)
3. API routes (`src/app/api/`)
4. Components (`src/components/`)
5. Pages (`src/app/`)

### 4. Common Fixes

**Supabase query typing:**
```typescript
// Wrong — untyped query
const { data } = await supabase.from('people').select('*');

// Fix — add .returns<Type>()
const { data } = await supabase
  .from('people')
  .select('id, name, current_toxicity_score')
  .returns<Array<{ id: string; name: string; current_toxicity_score: number }>>();
```

**Null handling:**
```typescript
// Wrong
const length = maybeString.length;

// Fix — optional chaining
const length = maybeString?.length ?? 0;
```

**Zod schema type extraction:**
```typescript
import { z } from 'zod';

const schema = z.object({ name: z.string() });
type SchemaType = z.infer<typeof schema>;
```

**AI response typing:**
```typescript
// Ensure tool_use block is typed
const toolUseBlock = response.content.find(
  (block): block is Anthropic.Messages.ToolUseBlock => block.type === 'tool_use'
);
```

## Type Locations

| Type Category | File |
|---------------|------|
| Analysis result types | `src/types/analysis.ts` |
| Database row types | `src/types/database.ts` |
| Person entity types | `src/types/person.ts` |
| AI engine schemas | `src/lib/ai/schemas.ts` |
| API request schemas | Inline in route files |

## After Fixing

1. Re-run `npx tsc --noEmit` to verify fixes
2. Run `pnpm lint` to catch any lint issues
3. Run `pnpm build` to verify full build succeeds
