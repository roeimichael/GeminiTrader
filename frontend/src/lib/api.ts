import type {
  AgentsResponse,
  HealthResponse,
  InitPoolRequest,
  InitPoolResponse,
  QueryRequest,
  QueryResponse,
  HistoryEntry,
} from '@/types/api';

const API_BASE_URL = 'http://localhost:8000';

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorDetails;
    try {
      errorDetails = await response.json();
    } catch {
      errorDetails = await response.text();
    }
    throw new ApiError(
      `API Error: ${response.statusText}`,
      response.status,
      errorDetails
    );
  }
  return response.json();
}

async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  return handleResponse<T>(response);
}

// API Functions
export const api = {
  // Health check
  getHealth: () => apiRequest<HealthResponse>('/api/health'),

  // Get available agents
  getAgents: () => apiRequest<AgentsResponse>('/api/agents'),

  // Initialize agent pool
  initializePool: (request: InitPoolRequest) =>
    apiRequest<InitPoolResponse>('/api/initialize-pool', {
      method: 'POST',
      body: JSON.stringify(request),
    }),

  // Execute analysis query
  query: (request: QueryRequest) =>
    apiRequest<QueryResponse>('/api/query', {
      method: 'POST',
      body: JSON.stringify(request),
    }),

  // Get conversation history
  getHistory: (sessionId?: string, limit: number = 10) => {
    const params = new URLSearchParams();
    if (sessionId) params.append('session_id', sessionId);
    params.append('limit', limit.toString());
    return apiRequest<HistoryEntry[]>(`/api/history?${params.toString()}`);
  },

  // Clear history
  clearHistory: (sessionId?: string) => {
    const params = sessionId ? `?session_id=${sessionId}` : '';
    return apiRequest<{ status: string }>(`/api/history${params}`, {
      method: 'DELETE',
    });
  },

  // Delete session
  deleteSession: (sessionId: string) =>
    apiRequest<{ status: string }>(`/api/session/${sessionId}`, {
      method: 'DELETE',
    }),

  // List active sessions
  listSessions: () =>
    apiRequest<{ sessions: string[]; count: number }>('/api/sessions'),
};

export { ApiError };
