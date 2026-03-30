import { z } from 'zod';
import { ICON_KEYS } from '../icon-keys';

export const toxicTraitSchema = z.object({
  name: z.string().describe('Name of the toxic trait, e.g. "Gaslighting", "Love Bombing"'),
  severity: z.enum(['low', 'moderate', 'high', 'critical']).describe('How severe this trait is'),
  description: z.string().describe('One-sentence explanation of this specific trait in this person. Do not describe how traits interact — that goes in pattern_analysis.'),
  icon: z.enum(ICON_KEYS).describe('Icon key: brain, shield, pulse, eye, warning, heart, fingerprint, or document'),
});

export const protectionStrategySchema = z.object({
  title: z.string().describe('Short strategy name, e.g. "The Grey Rock Method"'),
  description: z.string().describe('Actionable explanation of how to use this strategy'),
  priority: z.enum(['essential', 'recommended', 'optional']).describe('essential = immediate low-effort action, recommended = medium-term boundary change, optional = structural life change if patterns persist'),
});

export const selfReflectionSchema = z.object({
  message: z.string().describe('A compassionate message explaining this person is not showing toxic patterns'),
  suggestions: z.array(z.string()).min(2).max(4).describe('2-4 suggestions written as direct advice using imperative voice ("Consider...", "Try...", "Reflect on..."). Address the reader directly.'),
});

export const userPatternSchema = z.object({
  area: z.string().describe('Area of behavior, e.g. "Communication Style", "Boundary Setting", "Emotional Regulation"'),
  observation: z.string().describe('Specific observation written in second person ("You communicate clearly..."), about the person who submitted the analysis, NOT the subject'),
  sentiment: z.enum(['positive', 'neutral', 'needs_attention']).describe('Whether this pattern is healthy, neutral, or something to work on'),
  icon: z.enum(ICON_KEYS).describe('Icon key: brain (communication/thinking), shield (boundaries), pulse (emotional regulation), eye (awareness), warning (conflict), heart (relationships), fingerprint (identity), document (evidence-based)'),
});

export const userInsightSchema = z.object({
  communication_style: z.string().describe('1-2 sentence summary written in second person ("You communicate..."). For WhatsApp, analyze their actual messages. For text descriptions, analyze their framing and language choices.'),
  emotional_patterns: z.string().describe('Patterns written in second person ("You tend to...") — are they measured, reactive, catastrophizing, minimizing, etc.?'),
  boundary_awareness: z.enum(['strong', 'developing', 'weak']).describe('strong = recognizes violations, sets limits, communicates boundaries directly. developing = notices issues but inconsistent in enforcing. weak = does not recognize violations, people-pleases, avoids confrontation.'),
  detected_patterns: z.array(userPatternSchema).min(2).max(5).describe('2-5 specific behavioral patterns observed in the person who submitted the analysis'),
  growth_areas: z.array(z.string()).min(2).max(3).describe('2-3 actionable suggestions written in second person ("Consider...", "Try...")'),
  overall_tone: z.string().describe('Brief characterization of overall communication tone, e.g. "Measured but avoidant", "Assertive and clear", "Reactive and emotional"'),
});

export const analysisResultSchema = z.object({
  toxicity_score: z.number().describe('Toxicity score from 0.0 to 10.0'),
  risk_level: z.enum(['low', 'moderate', 'high']).describe('Overall risk level'),
  is_toxic: z.boolean().describe('Whether the person exhibits toxic behavioral patterns. Set to false if their behavior is within normal healthy dynamics.'),
  detected_traits: z.array(toxicTraitSchema).min(1).max(6).describe('1-6 detected behavioral traits'),
  pattern_analysis: z.string().describe('2-3 sentence analysis of how detected traits INTERACT as a system. Do not repeat individual trait descriptions — synthesize the bigger picture.'),
  protection_strategies: z.array(protectionStrategySchema).length(3).describe('Exactly 3 protection strategies with escalating commitment: essential (immediate), recommended (medium-term), optional (structural change)'),
  self_reflection: selfReflectionSchema.nullable().describe('If is_toxic is false, provide self-reflection. If is_toxic is true, set to null.'),
  headline: z.string().describe('Witty shareable phrase — a roast or meme caption. Does NOT start with "The". e.g. "Olympic-Level Gaslighter", "Certified Emotional Vampire", "Harmless Drama Minor". MUST be different from threat_type and tagline.'),
  tagline: z.string().describe('Short italic subtitle that complements the headline — explains the "why" behind the headline. Must NOT repeat words from headline or threat_type. e.g. "Rewrites reality like it\'s a hobby"'),
  threat_type: z.string().describe('Classified dossier codename — a 2-4 word archetype ALWAYS starting with "The". e.g. "The Puppet Master", "The Reality Bender", "The Gentle Giant". MUST be completely different from headline — no overlapping words.'),
  user_insight: userInsightSchema.describe("Analysis of the submitter's own behavioral patterns visible in their input. Written in second person. This is about the person submitting the analysis, NOT the subject being analyzed."),
});

// Convert Zod schema to JSON Schema using Zod v4 built-in method
export function zodToJsonSchema(schema: z.ZodType): Record<string, unknown> {
  return z.toJSONSchema(schema) as Record<string, unknown>;
}
