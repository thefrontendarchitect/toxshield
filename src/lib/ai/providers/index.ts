import type { LLMProvider } from './types';

export type ProviderName = 'openai' | 'anthropic';

let cachedProvider: LLMProvider | null = null;

export async function getProvider(): Promise<LLMProvider> {
  if (cachedProvider) return cachedProvider;

  const providerName = (process.env.ACTIVE_LLM_PROVIDER || 'openai') as ProviderName;

  switch (providerName) {
    case 'openai': {
      const { OpenAIProvider } = await import('./openai');
      cachedProvider = new OpenAIProvider();
      break;
    }
    case 'anthropic': {
      const { AnthropicProvider } = await import('./anthropic');
      cachedProvider = new AnthropicProvider();
      break;
    }
    default:
      throw new Error(
        `Unknown LLM provider: "${providerName}". Set ACTIVE_LLM_PROVIDER to "openai" or "anthropic".`
      );
  }

  return cachedProvider!;
}

export type { LLMProvider } from './types';
