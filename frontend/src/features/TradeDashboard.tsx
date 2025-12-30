import { useSessionStore } from '@/store/sessionStore';
import { useInitializePool } from '@/hooks/useApi';
import { AgentSelector } from '@/components/AgentSelector';
import { AnalysisInput } from '@/components/AnalysisInput';
import { AnalysisResults } from '@/components/AnalysisResults';
import { AnalyzingLoader } from '@/components/AnalyzingLoader';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Play, Loader2, CheckCircle2, Zap, RefreshCw } from 'lucide-react';

export function TradeDashboard() {
  const { appState, selectedAgents, sessionId, reset } = useSessionStore();
  const { mutate: initializePool, isPending: isInitializing } = useInitializePool();

  const handleInitialize = () => {
    if (selectedAgents.length === 0) return;
    initializePool({ selected_agents: selectedAgents });
  };

  const handleReset = () => {
    reset();
  };

  const isPoolReady = appState === 'ready' || appState === 'analyzing' || appState === 'results';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Trade Analysis</h1>
          <p className="text-muted-foreground">
            Multi-agent AI stock analysis powered by Gemini
          </p>
        </div>
        {sessionId && (
          <div className="flex items-center gap-3">
            <div className="text-xs text-muted-foreground font-mono">
              Session: {sessionId.slice(0, 8)}...
            </div>
            <Button variant="outline" size="sm" onClick={handleReset} className="gap-2">
              <RefreshCw className="w-4 h-4" />
              Reset
            </Button>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Agent Selection */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="gradient-card border-border/50">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Zap className="w-5 h-5 text-primary" />
                    Agent Selection
                  </CardTitle>
                  <CardDescription>
                    Select the AI agents to include in your analysis team
                  </CardDescription>
                </div>
                {isPoolReady && (
                  <div className="flex items-center gap-2 text-sm text-primary">
                    <CheckCircle2 className="w-4 h-4" />
                    Pool Ready
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <AgentSelector />
              
              {!isPoolReady && (
                <>
                  <Separator className="my-6" />
                  <Button
                    onClick={handleInitialize}
                    disabled={selectedAgents.length === 0 || isInitializing}
                    size="lg"
                    className="w-full gap-2"
                  >
                    {isInitializing ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Initializing Agents...
                      </>
                    ) : (
                      <>
                        <Play className="w-5 h-5" />
                        Start Session ({selectedAgents.length} agents)
                      </>
                    )}
                  </Button>
                </>
              )}
            </CardContent>
          </Card>

          {/* Analysis Results */}
          {appState === 'analyzing' && (
            <Card className="gradient-card border-border/50">
              <CardContent className="pt-6">
                <AnalyzingLoader />
              </CardContent>
            </Card>
          )}

          {appState === 'results' && (
            <Card className="gradient-card border-border/50">
              <CardContent className="pt-6">
                <AnalysisResults />
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right Column: Analysis Input */}
        <div className="space-y-6">
          <Card className="gradient-card border-border/50 sticky top-6">
            <CardHeader>
              <CardTitle>Run Analysis</CardTitle>
              <CardDescription>
                Enter a stock ticker and your question
              </CardDescription>
            </CardHeader>
            <CardContent>
              <AnalysisInput />
            </CardContent>
          </Card>

          {/* Quick Tips */}
          <Card className="gradient-card border-border/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Quick Tips</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground space-y-2">
              <p>• Select at least 2-3 agents for balanced analysis</p>
              <p>• Include both Bull and Bear researchers for debate</p>
              <p>• Add Risk Manager for final recommendations</p>
              <p>• Analysis takes 30-60 seconds to complete</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
