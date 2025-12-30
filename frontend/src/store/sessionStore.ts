import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { AppState, QueryResponse } from '@/types/api';

interface SessionStore {
  sessionId: string | null;
  selectedAgents: string[];
  appState: AppState;
  analysisResult: QueryResponse | null;
  
  // Actions
  setSessionId: (id: string) => void;
  setSelectedAgents: (agents: string[]) => void;
  toggleAgent: (agentKey: string) => void;
  setAppState: (state: AppState) => void;
  setAnalysisResult: (result: QueryResponse | null) => void;
  reset: () => void;
}

const initialState = {
  sessionId: null,
  selectedAgents: [],
  appState: 'idle' as AppState,
  analysisResult: null,
};

export const useSessionStore = create<SessionStore>()(
  persist(
    (set, get) => ({
      ...initialState,

      setSessionId: (id) => set({ sessionId: id }),
      
      setSelectedAgents: (agents) => set({ selectedAgents: agents }),
      
      toggleAgent: (agentKey) => {
        const current = get().selectedAgents;
        const isSelected = current.includes(agentKey);
        set({
          selectedAgents: isSelected
            ? current.filter((a) => a !== agentKey)
            : [...current, agentKey],
        });
      },
      
      setAppState: (state) => set({ appState: state }),
      
      setAnalysisResult: (result) => set({ analysisResult: result }),
      
      reset: () => set(initialState),
    }),
    {
      name: 'gemini-trader-session',
      partialize: (state) => ({
        sessionId: state.sessionId,
        selectedAgents: state.selectedAgents,
      }),
    }
  )
);
