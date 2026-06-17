# LLM Provider Configuration Reference

Quick reference for OpenAI-compatible LLM API endpoints. Useful when deploying apps that integrate multiple LLM providers.

## Provider Endpoints (OpenAI-Compatible)

| Provider | Base URL | Default Model | Env Var |
|----------|----------|---------------|---------|
| DashScope (通义千问) | `https://coding.dashscope.aliyuncs.com/v1` | `qwen3.7-plus` | `DASHSCOPE_API_KEY` |
| DashScope (standard) | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` | `DASHSCOPE_API_KEY` |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` | `DEEPSEEK_API_KEY` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4` | `OPENAI_API_KEY` |

## Important Notes

### DashScope Coding API vs Standard API

- **Coding API** (`coding.dashscope.aliyuncs.com`): For `sk-sp-` prefix keys, supports `qwen3.7-plus` etc. Chat completions only.
- **Standard API** (`dashscope.aliyuncs.com/compatible-mode`): For standard `sk-` prefix keys (console-generated), supports `qwen-plus`, `qwen-turbo`, AND `/embeddings`.
- **⚠️ Key types are NOT interchangeable**: `sk-sp-` keys work for chat on the coding endpoint but return 401 on `/embeddings`. For embedding, use standard console keys with the standard endpoint.
- The coding API endpoint is NOT documented officially — discovered through Hermes Agent usage

### DeepSeek Models

- `deepseek-v4-flash`: Fast, cheap, good for simple tasks
- `deepseek-v4-pro`: More capable, slower
- `deepseek-chat`: Alias for latest chat model

### TypeScript Integration Pattern

```typescript
import OpenAI from 'openai'

const PROVIDERS: Record<string, { baseURL: string; defaultModel: string }> = {
  dashscope: {
    baseURL: 'https://coding.dashscope.aliyuncs.com/v1',
    defaultModel: 'qwen3.7-plus',
  },
  deepseek: {
    baseURL: 'https://api.deepseek.com/v1',
    defaultModel: 'deepseek-v4-flash',
  },
}

function getLLMClient(provider: string, apiKey: string) {
  const config = PROVIDERS[provider]
  if (!config) throw new Error(`Unknown provider: ${provider}`)
  
  return new OpenAI({
    apiKey,
    baseURL: config.baseURL,
  })
}
```

### SSE Streaming Pattern

All OpenAI-compatible providers support SSE streaming:

```typescript
const stream = await client.chat.completions.create({
  model: selectedModel,
  messages: [{ role: 'user', content: userMessage }],
  stream: true,
})

for await (const chunk of stream) {
  const content = chunk.choices[0]?.delta?.content || ''
  // Send to client via SSE
  reply.write(`data: ${JSON.stringify({ content })}\n\n`)
}
reply.write('data: [DONE]\n\n')
```

### Environment Variable Naming Convention

Use provider-prefixed names to avoid conflicts:
- `DASHSCOPE_API_KEY` (not `LLM_API_KEY`)
- `DEEPSEEK_API_KEY`
- `OPENAI_API_KEY`

Legacy apps may use `LLM_API_KEY` + `LLM_PROVIDER` to select one provider at a time.
