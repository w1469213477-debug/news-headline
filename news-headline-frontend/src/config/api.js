export const apiConfig = {
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
}

export const aiChatConfig = {
  apiEndpoint: import.meta.env.VITE_AI_API_ENDPOINT || 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
  apiKey: import.meta.env.VITE_AI_API_KEY || '',
  model: import.meta.env.VITE_AI_MODEL || 'qwen3-max-preview',
}
