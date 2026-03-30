import { createClient } from '@/lib/supabase/server';
import { NextResponse } from 'next/server';

export async function GET() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { data: pack } = await supabase
    .from('purchases')
    .select('pack_type, analyses_remaining, analyses_granted, expires_at')
    .eq('user_id', user.id)
    .eq('status', 'completed')
    .gt('analyses_remaining', 0)
    .gt('expires_at', new Date().toISOString())
    .order('expires_at', { ascending: true })
    .limit(1)
    .maybeSingle();

  if (!pack) {
    return NextResponse.json({ active: false });
  }

  return NextResponse.json({ active: true, ...pack });
}
