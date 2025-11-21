import axios from 'axios';

export interface LLMInfo {
  llm_id: string;
  provider: string;
  name: string;
  description: string;
  avg_response_length: string;
  speed_rating: string;
  reasoning_model: boolean;
}

export interface ChatResponse {
  llm_id: string;
  content: string;
  timestamp: string;
  error?: string;
}

export interface BatchChatResponse {
  responses: ChatResponse[];
  timestamp: string;
}

// In a real app, this should be an environment variable
const API_URL = 'http://localhost:8000';

export const fetchLLMs = async (): Promise<LLMInfo[]> => {
  const response = await axios.get<{ llms: LLMInfo[] }>(`${API_URL}/api/v2/chat/llms`);
  return response.data.llms;
};

export const fetchBatchCompletion = async (prompt: string, llm_ids: string[]): Promise<ChatResponse[]> => {
  const response = await axios.post<BatchChatResponse>(`${API_URL}/api/v2/chat/completion/batch`, {
    prompt,
    llm_ids,
  });
  return response.data.responses;
};

export const fetchCompletion = async (prompt: string, llm_id: string): Promise<ChatResponse> => {
  const response = await axios.post<ChatResponse>(`${API_URL}/api/v2/chat/completion`, {
    prompt,
    llm_id,
  });
  return response.data;
};
