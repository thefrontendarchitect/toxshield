# API Patterns

**Authoritative source:** Root `AGENTS.md` and `src/app/api/analyze/route.ts`.

## Next.js API Route Pattern

```typescript
import { createClient } from '@/lib/supabase/server';
import { NextResponse } from 'next/server';
import { z } from 'zod';

const requestSchema = z.object({
  name: z.string().max(100),
  description: z.string().min(10).max(10000),
});

export async function POST(request: Request) {
  try {
    const supabase = await createClient();

    // 1. Auth check
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // 2. Validate input
    const body = await request.json();
    const parsed = requestSchema.safeParse(body);
    if (!parsed.success) {
      return NextResponse.json(
        { error: 'Invalid request', details: parsed.error.flatten() },
        { status: 400 }
      );
    }

    // 3. Business logic
    const result = await doSomething(parsed.data);

    // 4. Return response
    return NextResponse.json(result);
  } catch (error) {
    console.error('Error:', error);
    return NextResponse.json(
      { error: 'Something went wrong. Please try again.' },
      { status: 500 }
    );
  }
}
```

## Supabase Query Patterns

```typescript
// Type-safe select
const { data, error } = await supabase
  .from('people')
  .select('id, name, current_toxicity_score')
  .eq('user_id', user.id)
  .order('current_toxicity_score', { ascending: false })
  .returns<Array<{ id: string; name: string; current_toxicity_score: number }>>();

// Insert with return
const { data: person, error } = await supabase
  .from('people')
  .insert({ user_id: user.id, name, relationship } as Record<string, unknown>)
  .select('id')
  .returns<Array<{ id: string }>>()
  .single();

// Update
await supabase
  .from('people')
  .update({ current_toxicity_score: score } as Record<string, unknown>)
  .eq('id', personId);
```

## AI Integration Pattern

```typescript
import Anthropic from '@anthropic-ai/sdk';
import { analysisResultSchema, zodToJsonSchema } from './schemas';

const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY! });

// Structured output via tool_use
const response = await anthropic.messages.create({
  model: 'claude-sonnet-4-5-20250514',
  max_tokens: 2048,
  system: SYSTEM_PROMPT,
  messages: [{ role: 'user', content: userPrompt }],
  temperature: 0.7,
  tools: [{
    name: 'toxicity_analysis',
    description: 'Output the analysis result',
    input_schema: zodToJsonSchema(analysisResultSchema),
  }],
  tool_choice: { type: 'tool', name: 'toxicity_analysis' },
});

// Extract and validate
const toolUseBlock = response.content.find(b => b.type === 'tool_use');
const result = analysisResultSchema.parse(toolUseBlock.input);
```

## Environment Variables

| Variable | Server/Client | Purpose |
|----------|---------------|---------|
| `NEXT_PUBLIC_SUPABASE_URL` | Both | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Both | Supabase anonymous key |
| `ANTHROPIC_API_KEY` | Server only | Claude API key (NEVER expose to client) |
