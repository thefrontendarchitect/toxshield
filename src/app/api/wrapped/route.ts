import { createClient } from '@/lib/supabase/server';
import { NextResponse } from 'next/server';
import { computeWrappedData } from '@/lib/utils/wrapped';
import { AnalysisRow } from '@/types/database';
import { format, startOfMonth, endOfMonth, parse } from 'date-fns';

export async function GET(request: Request) {
  try {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    const url = new URL(request.url);
    const monthParam = url.searchParams.get('month'); // "2026-03"

    let monthDate: Date;
    if (monthParam) {
      if (!/^\d{4}-(?:0[1-9]|1[0-2])$/.test(monthParam)) {
        return NextResponse.json({ error: 'Invalid month format. Use YYYY-MM.' }, { status: 400 });
      }
      monthDate = parse(monthParam + '-01', 'yyyy-MM-dd', new Date());
    } else {
      // Default: previous month
      const now = new Date();
      monthDate = new Date(now.getFullYear(), now.getMonth() - 1, 1);
    }

    const monthStart = startOfMonth(monthDate);
    const monthEnd = endOfMonth(monthDate);
    const monthLabel = format(monthDate, 'MMMM yyyy');

    // Fetch analyses for this month with person names
    const { data: analyses } = await supabase
      .from('analyses')
      .select('*, people!inner(name)')
      .eq('user_id', user.id)
      .gte('created_at', monthStart.toISOString())
      .lte('created_at', monthEnd.toISOString())
      .order('created_at', { ascending: true });

    if (!analyses || analyses.length === 0) {
      return NextResponse.json({ wrapped: null, month: monthLabel });
    }

    // Map person names
    const mapped = analyses.map((a: Record<string, unknown>) => ({
      ...a,
      person_name: (a.people as { name: string })?.name ?? 'Unknown',
    }));

    const wrapped = computeWrappedData(mapped as (AnalysisRow & { person_name: string })[], monthLabel);

    return NextResponse.json({ wrapped, month: monthLabel });
  } catch (error) {
    console.error('Wrapped error:', error);
    return NextResponse.json({ error: 'Failed to generate wrapped' }, { status: 500 });
  }
}
