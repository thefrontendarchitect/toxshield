import Anthropic from '@anthropic-ai/sdk';
import { analysisResultSchema, zodToJsonSchema } from './schemas';
import { SYSTEM_PROMPT, buildUserPrompt, buildContextualPrompt, buildWhatsAppPrompt } from './prompts';
import { AnalysisResult } from '@/types/analysis';

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY!,
});

const MODEL = 'claude-sonnet-4-5-20250514';

interface AnalyzeParams {
  description: string;
  name: string;
  relationship: string | null;
  inputType?: 'text_description' | 'whatsapp_chat';
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
  } else {
    userPrompt = buildUserPrompt(description, name, relationship);
  }

  const jsonSchema = zodToJsonSchema(analysisResultSchema);

  const response = await anthropic.messages.create({
    model: MODEL,
    max_tokens: 2048,
    system: SYSTEM_PROMPT,
    messages: [
      {
        role: 'user',
        content: userPrompt,
      },
    ],
    temperature: 0.7,
    // Use structured output via tool_use pattern for reliable JSON
    tools: [
      {
        name: 'toxicity_analysis',
        description: 'Output the complete toxicity analysis result',
        input_schema: jsonSchema as Anthropic.Messages.Tool.InputSchema,
      },
    ],
    tool_choice: { type: 'tool', name: 'toxicity_analysis' },
  });

  // Extract the tool use result
  const toolUseBlock = response.content.find(
    (block) => block.type === 'tool_use'
  );

  if (!toolUseBlock || toolUseBlock.type !== 'tool_use') {
    throw new Error('AI did not return a structured analysis result');
  }

  // Validate with Zod
  const parsed = analysisResultSchema.parse(toolUseBlock.input);

  return {
    result: parsed,
    model: MODEL,
    promptTokens: response.usage.input_tokens,
    completionTokens: response.usage.output_tokens,
  };
}
