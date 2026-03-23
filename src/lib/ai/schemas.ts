import { z } from 'zod';

export const toxicTraitSchema = z.object({
  name: z.string().describe('Name of the toxic trait, e.g. "Gaslighting", "Love Bombing"'),
  severity: z.enum(['low', 'moderate', 'high', 'critical']).describe('How severe this trait is'),
  description: z.string().describe('One-sentence explanation specific to this person'),
  icon: z.string().describe('Single emoji that represents this trait'),
});

export const protectionStrategySchema = z.object({
  title: z.string().describe('Short strategy name, e.g. "The Grey Rock Method"'),
  description: z.string().describe('Actionable explanation of how to use this strategy'),
  priority: z.enum(['essential', 'recommended', 'optional']).describe('How important this strategy is'),
});

export const selfReflectionSchema = z.object({
  message: z.string().describe('A compassionate message explaining this person is not showing toxic patterns'),
  suggestions: z.array(z.string()).describe('2-4 suggestions for how the user might adjust their own approach'),
});

export const analysisResultSchema = z.object({
  toxicity_score: z.number().describe('Toxicity score from 0.0 to 10.0'),
  risk_level: z.enum(['low', 'moderate', 'high']).describe('Overall risk level'),
  is_toxic: z.boolean().describe('Whether the person exhibits toxic behavioral patterns. Set to false if their behavior is within normal healthy dynamics.'),
  detected_traits: z.array(toxicTraitSchema).describe('1-6 detected behavioral traits'),
  pattern_analysis: z.string().describe('2-3 sentence forensic behavioral pattern analysis'),
  protection_strategies: z.array(protectionStrategySchema).describe('Exactly 3 actionable protection strategies'),
  self_reflection: selfReflectionSchema.nullable().describe('If is_toxic is false, provide self-reflection. If is_toxic is true, set to null.'),
  headline: z.string().describe('Witty, shareable headline, e.g. "Olympic-Level Gaslighter" or "Certified Emotional Vampire"'),
  tagline: z.string().describe('Short witty one-liner for share cards'),
});

// Convert Zod schema to JSON Schema using Zod v4 built-in method
export function zodToJsonSchema(schema: z.ZodType): Record<string, unknown> {
  return z.toJSONSchema(schema) as Record<string, unknown>;
}
