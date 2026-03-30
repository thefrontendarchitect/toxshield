import { createHash } from 'crypto';
import { NextResponse } from 'next/server';
import { z } from 'zod';
import { getProvider } from '@/lib/ai/providers';

const requestSchema = z.object({
  description: z.string().min(5).max(500),
});

const quickResultSchema = z.object({
  verdict: z.enum(['RED_FLAG', 'YELLOW_FLAG', 'GREEN_FLAG']),
  explanation: z.string(),
  headline: z.string(),
  pattern_name: z.string(),
  score: z.number(),
});

const QUICK_SYSTEM_PROMPT = `You are ToxShield, a forensic behavioral analyst. You assess a single incident or behavior description and classify it as a red flag, yellow flag, or green flag.

## CLASSIFICATION
- RED_FLAG: Clear toxic/manipulative behavior. Gaslighting, DARVO, coercive control, emotional abuse, boundary violation.
- YELLOW_FLAG: Concerning but ambiguous. Could be stress, miscommunication, or an isolated incident. Worth watching.
- GREEN_FLAG: Normal/healthy behavior. Disagreements, setting boundaries, honest feedback, needing space.

## SCORING
- GREEN_FLAG: 0.0-3.0
- YELLOW_FLAG: 3.1-6.0
- RED_FLAG: 6.1-10.0

## RULES
1. Be direct and specific. Name the pattern if you recognize one.
2. One-sentence explanation only.
3. Headline should be witty and 3-6 words.
4. pattern_name should name the specific behavioral pattern (e.g. "DARVO", "Gaslighting", "Guilt-Tripping", "Healthy Boundary", "Normal Disagreement").`;

// Reuse rate-limiting pattern from try-analyze
const MAX_MAP_SIZE = 10000;
const rateLimitMap = new Map<string, { count: number; resetAt: number }>();
const RATE_LIMIT = 20; // Higher limit since these are cheaper
const RATE_WINDOW = 60 * 60 * 1000;

function hashIp(ip: string): string {
  return createHash('sha256').update(ip).digest('hex');
}

function checkRateLimit(ipHash: string): boolean {
  const now = Date.now();
  const entry = rateLimitMap.get(ipHash);

  if (!entry || now > entry.resetAt) {
    if (rateLimitMap.size >= MAX_MAP_SIZE) {
      for (const [key, val] of rateLimitMap) {
        if (now > val.resetAt) rateLimitMap.delete(key);
      }
    }
    rateLimitMap.set(ipHash, { count: 1, resetAt: now + RATE_WINDOW });
    return true;
  }

  if (entry.count >= RATE_LIMIT) return false;
  entry.count++;
  return true;
}

export async function POST(request: Request) {
  try {
    let body: unknown;
    try {
      body = await request.json();
    } catch {
      return NextResponse.json({ error: 'Invalid JSON body' }, { status: 400 });
    }

    const parsed = requestSchema.safeParse(body);
    if (!parsed.success) {
      return NextResponse.json(
        { error: 'Invalid request', details: parsed.error.flatten() },
        { status: 400 }
      );
    }

    const rawIp =
      request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() ||
      request.headers.get('x-real-ip') ||
      'unknown';
    const ipHash = hashIp(rawIp);

    if (!checkRateLimit(ipHash)) {
      return NextResponse.json(
        { error: 'Rate limit exceeded. Sign up for unlimited analyses.' },
        { status: 429 }
      );
    }

    const { description } = parsed.data;

    const provider = await getProvider();
    const jsonSchema = z.toJSONSchema(quickResultSchema) as Record<string, unknown>;

    const { result: rawResult } = await provider.call({
      systemPrompt: QUICK_SYSTEM_PROMPT,
      userPrompt: `Assess this situation:\n\n"${description}"`,
      jsonSchema,
      maxTokens: 512,
      temperature: 0.5,
    });

    const result = quickResultSchema.parse(rawResult);

    return NextResponse.json({ result });
  } catch (error) {
    console.error('Quick-assess error:', error);
    return NextResponse.json(
      { error: 'Assessment failed. Please try again.' },
      { status: 500 }
    );
  }
}
