import { getProvider } from './providers';
import { analysisResultSchema, zodToJsonSchema } from './schemas';
import { SYSTEM_PROMPT, buildUserPrompt, buildContextualPrompt, buildWhatsAppPrompt, buildSlackPrompt } from './prompts';
import { AnalysisResult } from '@/types/analysis';

interface AnalyzeParams {
  description: string;
  name: string;
  relationship: string | null;
  inputType?: 'text_description' | 'whatsapp_chat' | 'slack_chat';
  previousInputs?: Array<{ type: string; content: string; date: string }>;
  previousAnalysis?: {
    toxicity_score: number;
    detected_traits: Array<{ name: string }>;
    pattern_analysis: string;
  } | null;
}

interface AnalyzeResponse {
  result: AnalysisResult;
  model: string;
  promptTokens: number;
  completionTokens: number;
}

export async function analyzePersonality({
  description,
  name,
  relationship,
  inputType = 'text_description',
  previousInputs,
  previousAnalysis,
}: AnalyzeParams): Promise<AnalyzeResponse> {
  // Build the appropriate prompt based on input type
  let userPrompt: string;

  if (previousInputs && previousInputs.length > 0) {
    userPrompt = buildContextualPrompt(
      description,
      name,
      relationship,
      previousInputs,
      previousAnalysis ?? null
    );
  } else if (inputType === 'whatsapp_chat') {
    userPrompt = buildWhatsAppPrompt(description, name, relationship);
  } else if (inputType === 'slack_chat') {
    userPrompt = buildSlackPrompt(description, name, relationship);
  } else {
    userPrompt = buildUserPrompt(description, name, relationship);
  }

  const jsonSchema = zodToJsonSchema(analysisResultSchema);
  const provider = await getProvider();

  const { result: rawResult, model, promptTokens, completionTokens } =
    await provider.call({
      systemPrompt: SYSTEM_PROMPT,
      userPrompt,
      jsonSchema,
      maxTokens: 3072,
      temperature: 0.7,
    });

  // Validate with Zod regardless of provider
  const result = analysisResultSchema.parse(rawResult);

  return { result, model, promptTokens, completionTokens };
}
