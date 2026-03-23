import Anthropic from '@anthropic-ai/sdk';
import type { LLMProvider, LLMCallParams, LLMCallResult } from './types';

const MODEL = 'claude-sonnet-4-5-20250514';

export class AnthropicProvider implements LLMProvider {
  name = 'anthropic';
  private client: Anthropic;

  constructor() {
    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) throw new Error('ANTHROPIC_API_KEY environment variable is required');
    this.client = new Anthropic({ apiKey });
  }

  async call(params: LLMCallParams): Promise<LLMCallResult> {
    const response = await this.client.messages.create({
      model: MODEL,
      max_tokens: params.maxTokens,
      temperature: params.temperature,
      system: params.systemPrompt,
      messages: [{ role: 'user', content: params.userPrompt }],
      tools: [
        {
          name: 'toxicity_analysis',
          description: 'Output the complete toxicity analysis result',
          input_schema: params.jsonSchema as Anthropic.Messages.Tool.InputSchema,
        },
      ],
      tool_choice: { type: 'tool', name: 'toxicity_analysis' },
    });

    const toolUseBlock = response.content.find((b) => b.type === 'tool_use');
    if (!toolUseBlock || toolUseBlock.type !== 'tool_use') {
      throw new Error('Anthropic did not return a structured result');
    }

    return {
      result: toolUseBlock.input,
      model: MODEL,
      promptTokens: response.usage.input_tokens,
      completionTokens: response.usage.output_tokens,
    };
  }
}
