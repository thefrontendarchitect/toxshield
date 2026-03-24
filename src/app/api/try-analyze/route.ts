import { createHash } from 'crypto';
import { analyzePersonality } from '@/lib/ai/engine';
import { NextResponse } from 'next/server';
import { z } from 'zod';

const requestSchema = z.object({
  name: z.string().trim().max(100).default(''),
  relationship: z.string().trim().nullable(),
  description: z.string().min(10).max(50000),
  inputType: z
    .enum(['text_description', 'whatsapp_chat'])
    .default('text_description'),
});

// In-memory rate limiter — not durable across serverless instances.
// Intentionally unauthenticated — demo/try endpoint. Rate limited by IP only.
const MAX_MAP_SIZE = 10000;
const rateLimitMap = new Map<string, { count: number; resetAt: number }>();
const RATE_LIMIT = 10;
const RATE_WINDOW = 60 * 60 * 1000; // 1 hour

function hashIp(ip: string): string {
  return createHash('sha256').update(ip).digest('hex');
}

function checkRateLimit(ipHash: string): boolean {
  const now = Date.now();
  const entry = rateLimitMap.get(ipHash);

  if (!entry || now > entry.resetAt) {
    // Evict expired entries if map is too large
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
    // Rate limit by hashed IP
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

    let body: unknown;
    try {
      body = await request.json();
    } catch {
      return NextResponse.json(
        { error: 'Invalid JSON body' },
        { status: 400 }
      );
    }

    const parsed = requestSchema.safeParse(body);

    if (!parsed.success) {
      return NextResponse.json(
        { error: 'Invalid request', details: parsed.error.flatten() },
        { status: 400 }
      );
    }

    const { name, relationship, description, inputType } = parsed.data;

    // Run AI analysis — no auth, no DB, no context from previous analyses
    const { result, model, promptTokens, completionTokens } =
      await analyzePersonality({
        description,
        name,
        relationship: relationship || null,
        inputType,
      });

    console.log('[try-analyze] tokens:', {
      model,
      promptTokens,
      completionTokens,
      ipHash: ipHash.slice(0, 8),
    });

    return NextResponse.json({ result });
  } catch (error) {
    console.error('Try-analyze error:', error);
    return NextResponse.json(
      { error: 'Analysis failed. Please try again.' },
      { status: 500 }
    );
  }
}
