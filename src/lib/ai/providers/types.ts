export interface LLMCallParams {
  systemPrompt: string;
  userPrompt: string;
  jsonSchema: Record<string, unknown>;
  maxTokens: number;
  temperature: number;
}

export interface LLMCallResult {
  result: unknown;
  model: string;
  promptTokens: number;
  completionTokens: number;
}

export interface LLMProvider {
  name: string;
  call(params: LLMCallParams): Promise<LLMCallResult>;
}
