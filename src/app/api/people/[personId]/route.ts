import { createClient } from '@/lib/supabase/server';
import { NextResponse } from 'next/server';
import { z } from 'zod';

const updateSchema = z.object({
  name: z.string().min(1).max(100).optional(),
  relationship: z.string().nullable().optional(),
});

export async function PATCH(
  request: Request,
  { params }: { params: Promise<{ personId: string }> }
) {
  try {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { personId } = await params;

    const body = await request.json();
    const parsed = updateSchema.safeParse(body);

    if (!parsed.success) {
      return NextResponse.json(
        { error: 'Invalid request', details: parsed.error.flatten() },
        { status: 400 }
      );
    }

    // Build update object from provided fields
    const updates: Record<string, unknown> = {};
    if (parsed.data.name !== undefined) updates.name = parsed.data.name;
    if (parsed.data.relationship !== undefined) updates.relationship = parsed.data.relationship;

    if (Object.keys(updates).length === 0) {
      return NextResponse.json({ error: 'No fields to update' }, { status: 400 });
    }

    const { data: person, error } = await supabase
      .from('people')
      .update(updates)
      .eq('id', personId)
      .eq('user_id', user.id)
      .select('id, name, relationship')
      .returns<Array<{ id: string; name: string; relationship: string | null }>>()
      .single();

    if (error || !person) {
      return NextResponse.json({ error: 'Person not found' }, { status: 404 });
    }

    return NextResponse.json(person);
  } catch (error) {
    if (process.env.NODE_ENV === 'development') console.error('Update person error:', error);
    return NextResponse.json(
      { error: 'Update failed. Please try again.' },
      { status: 500 }
    );
  }
}

export async function DELETE(
  _request: Request,
  { params }: { params: Promise<{ personId: string }> }
) {
  try {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { personId } = await params;

    const { data: deleted, error } = await supabase
      .from('people')
      .delete()
      .eq('id', personId)
      .eq('user_id', user.id)
      .select('id')
      .single();

    if (error || !deleted) {
      return NextResponse.json({ error: 'Person not found' }, { status: 404 });
    }

    return new NextResponse(null, { status: 204 });
  } catch (error) {
    if (process.env.NODE_ENV === 'development') console.error('Delete person error:', error);
    return NextResponse.json(
      { error: 'Delete failed. Please try again.' },
      { status: 500 }
    );
  }
}
