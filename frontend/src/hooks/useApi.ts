import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, ApiError } from '@/lib/api';
import { useSessionStore } from '@/store/sessionStore';
import { toast } from 'sonner';
import type { InitPoolRequest, QueryRequest } from '@/types/api';

// Query Keys
export const queryKeys = {
  health: ['health'] as const,
  agents: ['agents'] as const,
  history: (sessionId?: string) => ['history', sessionId] as const,
  sessions: ['sessions'] as const,
};

// Get available agents
export function useAgents() {
  return useQuery({
    queryKey: queryKeys.agents,
    queryFn: api.getAgents,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

// Health check
export function useHealth() {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: api.getHealth,
    refetchInterval: 30000, // Poll every 30 seconds
  });
}

// Initialize pool
export function useInitializePool() {
  const queryClient = useQueryClient();
  const { setSessionId, setAppState } = useSessionStore();

  return useMutation({
    mutationFn: (request: InitPoolRequest) => api.initializePool(request),
    onSuccess: (data) => {
      setSessionId(data.session_id);
      setAppState('ready');
      toast.success(`${data.agent_count} agents initialized`, {
        description: data.message,
      });
      queryClient.invalidateQueries({ queryKey: queryKeys.sessions });
    },
    onError: (error: Error) => {
      setAppState('idle');
      const message = error instanceof ApiError 
        ? `${error.message} (${error.status})`
        : error.message;
      toast.error('Failed to initialize agents', { description: message });
    },
  });
}

// Run analysis query
export function useRunAnalysis() {
  const { setAppState, setAnalysisResult, sessionId } = useSessionStore();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: Omit<QueryRequest, 'session_id'>) =>
      api.query({ ...request, session_id: sessionId || undefined }),
    onMutate: () => {
      setAppState('analyzing');
    },
    onSuccess: (data) => {
      setAnalysisResult(data);
      setAppState('results');
      toast.success('Analysis complete', {
        description: `${data.ticker}: ${data.final_verdict.overall_recommendation}`,
      });
      queryClient.invalidateQueries({ queryKey: queryKeys.history(sessionId || undefined) });
    },
    onError: (error: Error) => {
      setAppState('ready');
      const message = error instanceof ApiError
        ? `${error.message} (${error.status})`
        : error.message;
      toast.error('Analysis failed', { description: message });
    },
  });
}

// Get history
export function useHistory(limit: number = 10) {
  const { sessionId } = useSessionStore();
  
  return useQuery({
    queryKey: queryKeys.history(sessionId || undefined),
    queryFn: () => api.getHistory(sessionId || undefined, limit),
    enabled: !!sessionId,
  });
}

// List sessions
export function useSessions() {
  return useQuery({
    queryKey: queryKeys.sessions,
    queryFn: api.listSessions,
  });
}

// Clear history
export function useClearHistory() {
  const queryClient = useQueryClient();
  const { sessionId } = useSessionStore();

  return useMutation({
    mutationFn: () => api.clearHistory(sessionId || undefined),
    onSuccess: () => {
      toast.success('History cleared');
      queryClient.invalidateQueries({ queryKey: queryKeys.history(sessionId || undefined) });
    },
    onError: (error: Error) => {
      toast.error('Failed to clear history', { description: error.message });
    },
  });
}

// Delete session
export function useDeleteSession() {
  const queryClient = useQueryClient();
  const { reset } = useSessionStore();

  return useMutation({
    mutationFn: (sessionId: string) => api.deleteSession(sessionId),
    onSuccess: () => {
      reset();
      toast.success('Session deleted');
      queryClient.invalidateQueries({ queryKey: queryKeys.sessions });
    },
    onError: (error: Error) => {
      toast.error('Failed to delete session', { description: error.message });
    },
  });
}
