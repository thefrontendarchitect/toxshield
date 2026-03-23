---
name: api-endpoint
description: Create a Next.js API route with Zod validation, Supabase integration, and proper auth. Use when adding new API endpoints.
argument-hint: [endpoint-name]
disable-model-invocation: true
allowed-tools: Write, Read, Glob, Grep, Edit
---

# Create API Endpoint

Create a complete Next.js API route following ToxShield patterns.

## Arguments

- `$0` - Endpoint name (kebab-case, e.g., `share-profile`, `export-data`)

## Files to Create/Modify

```
src/app/api/$0/
└── route.ts              # Next.js Route Handler
```

## Implementation Steps

1. **Create route handler** (`src/app/api/$0/route.ts`):
   - Define Zod request schema
   - Check Supabase auth
   - Implement business logic
   - Return NextResponse.json

2. **Add types if needed** (`src/types/$0.ts` or extend existing type files)

3. **Add Zod validation schema** (inline in route.ts or separate validation.ts)

## Templates

- [route.ts template](templates/route.ts.template)
- [types.ts template](templates/types.ts.template)
- [validation.ts template](templates/validation.ts.template)

## Pattern Reference

```typescript
import { createClient } from '@/lib/supabase/server';
import { NextResponse } from 'next/server';
import { z } from 'zod';

const requestSchema = z.object({
  // Define fields with validation
});

export async function POST(request: Request) {
  try {
    const supabase = await createClient();

    // Auth check
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Validate
    const body = await request.json();
    const parsed = requestSchema.safeParse(body);
    if (!parsed.success) {
      return NextResponse.json(
        { error: 'Invalid request', details: parsed.error.flatten() },
        { status: 400 }
      );
    }

    // Business logic + DB operations
    const { data, error } = await supabase
      .from('table')
      .select('*')
      .eq('user_id', user.id)
      .returns<Array<RowType>>();

    if (error) throw error;

    return NextResponse.json({ data });
  } catch (error) {
    console.error('Error:', error);
    return NextResponse.json(
      { error: 'Something went wrong.' },
      { status: 500 }
    );
  }
}
```

## Checklist

- [ ] Zod validation on request body
- [ ] Supabase auth check (`getUser()`)
- [ ] User isolation (`eq('user_id', user.id)`)
- [ ] Type-safe Supabase queries (`.returns<Type>()`)
- [ ] Proper error handling (try/catch, generic messages)
- [ ] Correct HTTP status codes (200, 201, 400, 401, 500)
- [ ] No secrets exposed in responses

## Example Usage

```
/api-endpoint share-profile
```

Creates `src/app/api/share-profile/route.ts` with full auth + validation + Supabase pattern.
