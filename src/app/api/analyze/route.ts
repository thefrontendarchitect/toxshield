import { createClient } from '@/lib/supabase/server';
import { analyzePersonality } from '@/lib/ai/engine';
import { updateStreakAfterAnalysis, checkAndAwardBadges } from '@/lib/utils/streaks';
import { FREE_LIMIT, getMonthStart } from '@/lib/utils/usage';
import { NextResponse } from 'next/server';
import { z } from 'zod';

const requestSchema = z.object({
  name: z.string().max(100).default(''),
  relationship: z.string().nullable(),
  description: z.string().min(10).max(50000),
  personId: z.string().uuid().optional(),
  inputType: z.enum(['text_description', 'whatsapp_chat', 'slack_chat']).default('text_description'),
});

export async function POST(request: Request) {
  try {
    const supabase = await createClient();

    // Check authentication
    const {
      data: { user },
    } = await supabase.auth.getUser();

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body = await request.json();
    const parsed = requestSchema.safeParse(body);

    if (!parsed.success) {
      return NextResponse.json(
        { error: 'Invalid request', details: parsed.error.flatten() },
        { status: 400 }
      );
    }

    let { name } = parsed.data;
    const { relationship: rawRelationship, description, personId, inputType } = parsed.data;
    let relationship = rawRelationship?.trim() || null;

    // Check usage limits (freemium gate)
    const monthStart = getMonthStart();
    const [{ data: usageRow }, { data: profile }] = await Promise.all([
      supabase.from('usage_tracking').select('*').eq('user_id', user.id).eq('period_start', monthStart).maybeSingle(),
      supabase.from('profiles').select('tier').eq('id', user.id).single(),
    ]);

    const tier = (profile as { tier?: string } | null)?.tier ?? 'free';
    if (tier === 'free') {
      const used = usageRow?.analyses_used ?? 0;
      const bonus = usageRow?.bonus_analyses ?? 0;
      const limit = FREE_LIMIT + bonus;
      if (used >= limit) {
        return NextResponse.json(
          { error: 'FREE_LIMIT_REACHED', usage: { used, limit, remaining: 0 } },
          { status: 402 }
        );
      }
    }

    // Resolve person: explicit personId, name-based dedup, or new person
    let previousInputs: Array<{ type: string; content: string; date: string }> = [];
    let previousAnalysis = null;
    let resolvedPersonId = personId;

    // If personId provided explicitly, use it
    if (resolvedPersonId) {
      const { data: existingPerson } = await supabase
        .from('people')
        .select('name, relationship')
        .eq('id', resolvedPersonId)
        .eq('user_id', user.id)
        .returns<Array<{ name: string; relationship: string | null }>>()
        .maybeSingle();

      if (existingPerson) {
        name = existingPerson.name;
        relationship = existingPerson.relationship;
      }
    }

    // Safety-net dedup: if no personId, check for existing person by name
    if (!resolvedPersonId && name) {
      const escapedName = name.replace(/[%_\\]/g, '\\$&');
      const { data: existingPeople } = await supabase
        .from('people')
        .select('id, name, relationship')
        .eq('user_id', user.id)
        .ilike('name', escapedName)
        .limit(1)
        .returns<Array<{ id: string; name: string; relationship: string | null }>>();

      if (existingPeople && existingPeople.length > 0) {
        resolvedPersonId = existingPeople[0].id;
      }
    }

    // Fetch prior context if we have an existing person (explicit or dedup-matched)
    if (resolvedPersonId) {
      const { data: inputs } = await supabase
        .from('inputs')
        .select('input_type, content, created_at')
        .eq('person_id', resolvedPersonId)
        .eq('user_id', user.id)
        .order('created_at', { ascending: true })
        .returns<Array<{ input_type: string; content: string; created_at: string }>>();

      if (inputs) {
        previousInputs = inputs.map((i) => ({
          type: i.input_type,
          content: i.content,
          date: i.created_at,
        }));
      }

      const { data: latestAnalysis } = await supabase
        .from('analyses')
        .select('toxicity_score, detected_traits, pattern_analysis')
        .eq('person_id', resolvedPersonId)
        .eq('user_id', user.id)
        .order('created_at', { ascending: false })
        .limit(1)
        .returns<Array<{ toxicity_score: number; detected_traits: Array<{ name: string }>; pattern_analysis: string }>>()
        .maybeSingle();

      if (latestAnalysis) {
        previousAnalysis = latestAnalysis;
      }
    }

    // Run AI analysis (with prior context if existing person)
    const { result, model, promptTokens, completionTokens } =
      await analyzePersonality({
        description,
        name,
        relationship,
        inputType,
        previousInputs: previousInputs.length > 0 ? previousInputs : undefined,
        previousAnalysis,
      });

    // Create person record if new (with placeholder scores — updated after analysis is saved)
    let actualPersonId = resolvedPersonId;
    const isNewPerson = !actualPersonId;

    if (isNewPerson) {
      const { data: person, error: personError } = await supabase
        .from('people')
        .insert({
          user_id: user.id,
          name,
          relationship,
          current_toxicity_score: 0,
          current_risk_level: 'low',
          is_toxic: false,
          analysis_count: 0,
        } as Record<string, unknown>)
        .select('id')
        .returns<Array<{ id: string }>>()
        .single();

      if (personError) {
        throw personError;
      }

      actualPersonId = person.id;
    }

    // Save analysis
    const { data: analysis, error: analysisError } = await supabase
      .from('analyses')
      .insert({
        person_id: actualPersonId,
        user_id: user.id,
        toxicity_score: result.toxicity_score,
        risk_level: result.risk_level,
        is_toxic: result.is_toxic,
        detected_traits: result.detected_traits,
        pattern_analysis: result.pattern_analysis,
        protection_strategies: result.protection_strategies,
        self_reflection: result.self_reflection,
        headline: result.headline,
        tagline: result.tagline,
        threat_type: result.threat_type,
        user_insight: result.user_insight,
        input_summary: description.substring(0, 200),
        model_used: model,
        prompt_tokens: promptTokens,
        completion_tokens: completionTokens,
      } as Record<string, unknown>)
      .select('id')
      .returns<Array<{ id: string }>>()
      .single();

    if (analysisError) {
      // Clean up the person record if we just created it
      if (isNewPerson) {
        await supabase.from('people').delete().eq('id', actualPersonId).eq('user_id', user.id);
      }
      throw analysisError;
    }

    // Save input
    const { error: inputError } = await supabase.from('inputs').insert({
      analysis_id: analysis.id,
      person_id: actualPersonId,
      user_id: user.id,
      input_type: inputType,
      content: description,
    } as Record<string, unknown>);

    if (inputError) {
      throw inputError;
    }

    // Update person with actual scores AFTER analysis + input are saved
    const { count: analysisCount } = await supabase
      .from('analyses')
      .select('*', { count: 'exact', head: true })
      .eq('person_id', actualPersonId)
      .eq('user_id', user.id);

    const { error: updateError } = await supabase
      .from('people')
      .update({
        current_toxicity_score: result.toxicity_score,
        current_risk_level: result.risk_level,
        is_toxic: result.is_toxic,
        current_threat_type: result.threat_type,
        analysis_count: analysisCount ?? 1,
      } as Record<string, unknown>)
      .eq('id', actualPersonId)
      .eq('user_id', user.id);

    if (updateError) {
      console.error('Failed to update person scores:', updateError);
    }

    // Increment usage counter
    await supabase.from('usage_tracking').upsert({
      user_id: user.id,
      period_start: monthStart,
      analyses_used: (usageRow?.analyses_used ?? 0) + 1,
      bonus_analyses: usageRow?.bonus_analyses ?? 0,
    } as Record<string, unknown>, { onConflict: 'user_id,period_start' });

    // Update streak + check badges (fire-and-forget — don't block response)
    updateStreakAfterAnalysis(supabase, user.id).then(async () => {
      const [{ data: s }, { count: peopleCount }, { count: allAnalysesCount }] = await Promise.all([
        supabase.from('streaks').select('current_streak').eq('user_id', user.id).maybeSingle(),
        supabase.from('people').select('*', { count: 'exact', head: true }).eq('user_id', user.id),
        supabase.from('analyses').select('*', { count: 'exact', head: true }).eq('user_id', user.id),
      ]);
      await checkAndAwardBadges(supabase, user.id, allAnalysesCount ?? 1, peopleCount ?? 1, s?.current_streak ?? 1);
    }).catch((err) => console.error('[post-analysis] streak/badge error:', err));

    return NextResponse.json({
      personId: actualPersonId,
      analysisId: analysis.id,
      result,
    });
  } catch (error) {
    console.error('Analysis error:', error);
    return NextResponse.json(
      { error: 'Analysis failed. Please try again.' },
      { status: 500 }
    );
  }
}
