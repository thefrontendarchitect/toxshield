import { createClient } from '@/lib/supabase/server';
import { NextResponse } from 'next/server';
import { HealthCheckinRow } from '@/types/database';
import { z } from 'zod';

const checkinSchema = z.object({
  mood: z.number().int().min(1).max(5),
  note: z.string().max(200).optional(),
});

export async function POST(request: Request) {
  try {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    const body = await request.json();
    const parsed = checkinSchema.safeParse(body);
    if (!parsed.success) {
      return NextResponse.json({ error: 'Invalid request', details: parsed.error.flatten() }, { status: 400 });
    }

    const today = new Date().toISOString().split('T')[0];

    // Upsert — one check-in per day
    const { data, error } = await supabase
      .from('health_checkins')
      .upsert({
        user_id: user.id,
        mood: parsed.data.mood,
        note: parsed.data.note ?? null,
        checked_in_at: today,
      } as Record<string, unknown>, { onConflict: 'user_id,checked_in_at' })
      .select('*')
      .returns<HealthCheckinRow>()
      .single();

    if (error) throw error;

    return NextResponse.json({ checkin: data });
  } catch (error) {
    console.error('Health check-in error:', error);
    return NextResponse.json({ error: 'Check-in failed' }, { status: 500 });
  }
}

export async function GET() {
  try {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    const { data: checkins } = await supabase
      .from('health_checkins')
      .select('*')
      .eq('user_id', user.id)
      .order('checked_in_at', { ascending: false })
      .limit(30)
      .returns<HealthCheckinRow[]>();

    return NextResponse.json({ checkins: checkins ?? [] });
  } catch (error) {
    console.error('Health check-in fetch error:', error);
    return NextResponse.json({ error: 'Failed to fetch check-ins' }, { status: 500 });
  }
}
