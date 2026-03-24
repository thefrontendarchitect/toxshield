import { createClient } from '@/lib/supabase/server';
import { NextResponse } from 'next/server';
import { z } from 'zod';

const querySchema = z.object({
  name: z.string().min(1).max(100),
});

export async function GET(request: Request) {
  try {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const parsed = querySchema.safeParse({ name: searchParams.get('name')?.trim() });

    if (!parsed.success) {
      return NextResponse.json({ matches: [] });
    }

    // Escape ilike metacharacters for exact case-insensitive match
    const escaped = parsed.data.name.replace(/[%_\\]/g, '\\$&');

    const { data: matches, error } = await supabase
      .from('people')
      .select('id, name, relationship, analysis_count')
      .eq('user_id', user.id)
      .ilike('name', escaped)
      .limit(10)
      .returns<Array<{ id: string; name: string; relationship: string | null; analysis_count: number }>>();

    if (error) throw error;

    return NextResponse.json({ matches: matches ?? [] });
  } catch (error) {
    console.error('People search error:', error);
    return NextResponse.json(
      { error: 'Search failed' },
      { status: 500 }
    );
  }
}
