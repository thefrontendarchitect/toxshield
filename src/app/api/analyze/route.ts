import { createClient } from '@/lib/supabase/server';
import { analyzePersonality } from '@/lib/ai/engine';
import { NextResponse } from 'next/server';
import { z } from 'zod';

const requestSchema = z.object({
  name: z.string().max(100).default(''),
  relationship: z.string().nullable(),
  description: z.string().min(10).max(50000),
  personId: z.string().uuid().optional(),
  inputType: z.enum(['text_description', 'whatsapp_chat']).default('text_description'),
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

    let { name, relationship: rawRelationship, description, personId, inputType } = parsed.data;
    let relationship = rawRelationship?.trim() || null;

    // If updating existing person, fetch context and person details
    let previousInputs: Array<{ type: string; content: string; date: string }> = [];
    let previousAnalysis = null;

    if (personId) {
      // Fetch person details for name/relationship (scoped to current user)
      const { data: existingPerson } = await supabase
        .from('people')
        .select('name, relationship')
        .eq('id', personId)
        .eq('user_id', user.id)
        .returns<Array<{ name: string; relationship: string | null }>>()
        .single();

      if (existingPerson) {
        name = existingPerson.name;
        relationship = existingPerson.relationship;
      }

      // Fetch all prior inputs (scoped to current user)
      const { data: inputs } = await supabase
        .from('inputs')
        .select('input_type, content, created_at')
        .eq('person_id', personId)
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

      // Fetch latest analysis (scoped to current user)
      const { data: latestAnalysis } = await supabase
        .from('analyses')
        .select('toxicity_score, detected_traits, pattern_analysis')
        .eq('person_id', personId)
        .eq('user_id', user.id)
        .order('created_at', { ascending: false })
        .limit(1)
        .returns<Array<{ toxicity_score: number; detected_traits: Array<{ name: string }>; pattern_analysis: string }>>()
        .single();

      if (latestAnalysis) {
        previousAnalysis = latestAnalysis;
      }
    }

    // Run AI analysis
    const { result, model, promptTokens, completionTokens } =
      await analyzePersonality({
        description,
        name,
        relationship,
        inputType,
        previousInputs: previousInputs.length > 0 ? previousInputs : undefined,
        previousAnalysis,
      });

    // Create or get person record
    let actualPersonId = personId;

    if (!actualPersonId) {
      const { data: person, error: personError } = await supabase
        .from('people')
        .insert({
          user_id: user.id,
          name,
          relationship,
          current_toxicity_score: result.toxicity_score,
          current_risk_level: result.risk_level,
          is_toxic: result.is_toxic,
          analysis_count: 1,
        } as Record<string, unknown>)
        .select('id')
        .returns<Array<{ id: string }>>()
        .single();

      if (personError) {
        throw personError;
      }

      actualPersonId = person.id;
    } else {
      // Update existing person's current scores (scoped to current user)
      await supabase
        .from('people')
        .update({
          current_toxicity_score: result.toxicity_score,
          current_risk_level: result.risk_level,
          is_toxic: result.is_toxic,
          analysis_count: previousInputs.length + 1,
        } as Record<string, unknown>)
        .eq('id', actualPersonId)
        .eq('user_id', user.id);
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
