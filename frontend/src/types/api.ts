// API Types generated from OpenAPI spec

export interface AgentInfo {
  name: string;
  description: string;
  category: string;
  requires_memory: boolean;
}

export interface AgentsResponse {
  [category: string]: {
    [key: string]: AgentInfo;
  };
}

export interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
  active_sessions: number;
}

export interface InitPoolRequest {
  selected_agents: string[];
  session_id?: string;
}

export interface InitPoolResponse {
  status: string;
  message: string;
  agent_count: number;
  session_id: string;
  agents: string[];
}

export interface QueryRequest {
  query: string;
  ticker: string;
  date?: string;
  session_id?: string;
}

export interface QueryClassification {
  selected_agents: string[];
  reasoning: string;
  complexity: string;
  estimated_cost: string;
  method: string;
}

export interface IndividualResponse {
  agent: string;
  category: string;
  perspective: string;
  response: string;
}

export interface DebateExchange {
  speaker: string;
  statement: string;
}

export interface DebateRound {
  round: number;
  topic: string;
  exchanges: DebateExchange[];
}

export interface SentimentBreakdown {
  bullish: number;
  bearish: number;
  neutral: number;
  bullish_percentage: number;
}

export interface FinalVerdict {
  timestamp: string;
  ticker: string;
  trade_date: string;
  overall_recommendation: 'BUY' | 'SELL' | 'HOLD';
  confidence_level: string;
  sentiment_breakdown: SentimentBreakdown;
  final_trade_decision: string;
  investment_plan: string;
  summary: string;
}

export interface QueryResponse {
  status: string;
  timestamp: string;
  query: string;
  ticker: string;
  query_classification: QueryClassification;
  individual_responses: IndividualResponse[];
  debate: DebateRound[];
  final_verdict: FinalVerdict;
}

export interface HistoryEntry {
  id: string;
  query: string;
  ticker: string;
  timestamp: string;
  recommendation: string;
}

export interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}

export interface HTTPValidationError {
  detail: ValidationError[];
}

// App State types
export type AppState = 'idle' | 'initializing' | 'ready' | 'analyzing' | 'results';

export interface SessionState {
  sessionId: string | null;
  selectedAgents: string[];
  state: AppState;
  analysisResult: QueryResponse | null;
}
