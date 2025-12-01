import axios from 'axios';

export interface LLMInfo {
  llm_id: string;
  provider: string;
  api_provider: string;
  name: string;
  description: string;
  avg_response_length: string;
  speed_rating: string;
  reasoning_model: boolean;
}

export interface LLMSelectionPayload {
  llm_id: string;
  api_provider: string;
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
// const API_URL = 'http://localhost:8000';
const API_URL = 'https://competing-llm-arena.vercel.app';

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in?: number;
  expires_at?: string;
}

export interface AuthResponse {
  user_id: string;
  email: string;
  tokens: AuthTokens;
}

export interface AuthLogoutResponse {
  revoked: boolean;
  message: string;
}

const authHeaders = (token?: string) =>
  token
    ? {
        Authorization: `Bearer ${token}`,
      }
    : undefined;

export const fetchLLMs = async (): Promise<LLMInfo[]> => {
  const response = await axios.get<{ llms: LLMInfo[] }>(`${API_URL}/api/v2/chat/llms`);
  return response.data.llms;
};

export const fetchBatchCompletion = async (prompt: string, llms: LLMSelectionPayload[], accessToken?: string): Promise<ChatResponse[]> => {
  const response = await axios.post<BatchChatResponse>(
    `${API_URL}/api/v2/chat/completion/batch`,
    { prompt, llms },
    { headers: authHeaders(accessToken) }
  );
  return response.data.responses;
};

export const fetchCompletion = async (
  prompt: string,
  selection: LLMSelectionPayload,
  accessToken?: string
): Promise<ChatResponse> => {
  const response = await axios.post<ChatResponse>(
    `${API_URL}/api/v2/chat/completion`,
    { prompt, llm_id: selection.llm_id, api_provider: selection.api_provider },
    { headers: authHeaders(accessToken) }
  );
  return response.data;
};

export const login = async (email: string, password: string): Promise<AuthResponse> => {
  const response = await axios.post<AuthResponse>(`${API_URL}/api/auth/login`, { email, password });
  return response.data;
};

export const refreshSession = async (refreshToken: string): Promise<AuthTokens> => {
  const response = await axios.post<AuthTokens>(`${API_URL}/api/auth/refresh`, { refresh_token: refreshToken });
  return response.data;
};

export const logout = async (accessToken: string): Promise<AuthLogoutResponse> => {
  const response = await axios.post<AuthLogoutResponse>(
    `${API_URL}/api/auth/logout`,
    { access_token: accessToken },
    { headers: authHeaders(accessToken) }
  );
  return response.data;
};
