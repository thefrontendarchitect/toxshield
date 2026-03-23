import OpenAI from 'openai';
import type { LLMProvider, LLMCallParams, LLMCallResult } from './types';

const MODEL = 'gpt-4o';

export class OpenAIProvider implements LLMProvider {
  name = 'openai';
  private client: OpenAI;

  constructor() {
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) throw new Error('OPENAI_API_KEY environment variable is required');
    this.client = new OpenAI({ apiKey });
  }

  async call(params: LLMCallParams): Promise<LLMCallResult> {
    const response = await this.client.chat.completions.create({
      model: MODEL,
      max_tokens: params.maxTokens,
      temperature: params.temperature,
      messages: [
        { role: 'system', content: params.systemPrompt },
        { role: 'user', content: params.userPrompt },
      ],
      response_format: {
        type: 'json_schema',
        json_schema: {
          name: 'toxicity_analysis',
          strict: true,
          schema: params.jsonSchema,
        },
      },
    });

    const content = response.choices[0]?.message?.content;
    if (!content) throw new Error('OpenAI returned no content');

    const result = JSON.parse(content);

    return {
      result,
      model: MODEL,
      promptTokens: response.usage?.prompt_tokens ?? 0,
      completionTokens: response.usage?.completion_tokens ?? 0,
    };
  }
}
