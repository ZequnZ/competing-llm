import axios from 'axios';

export interface LLMInfo {
  llm_id: number;
  name: string;
  description: string;
  avg_response_length: string;
  speed_rating: string;
}

export interface ChatResponse {
  llm_id: number;
  prompt: string;
  content: string;
  timestamp: string;
}

export interface BatchChatResponse {
  responses: ChatResponse[];
  timestamp: string;
}

// In a real app, this should be an environment variable
const API_URL = 'http://localhost:8000';

export const fetchLLMs = async (): Promise<LLMInfo[]> => {
  const response = await axios.get<{ llms: LLMInfo[] }>(`${API_URL}/api/chat/llms`);
  return response.data.llms;
};

export const fetchBatchCompletion = async (prompt: string, llm_ids: number[]): Promise<ChatResponse[]> => {
  const response = await axios.post<BatchChatResponse>(`${API_URL}/api/chat/completion/batch`, {
    prompt,
    llm_ids,
  });
  return response.data.responses;
};

