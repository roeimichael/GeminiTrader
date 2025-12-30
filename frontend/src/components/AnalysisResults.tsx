import { useSessionStore } from '@/store/sessionStore';
import { VerdictCard } from './VerdictCard';
import { DebateLog } from './DebateLog';
import { AgentResponses } from './AgentResponses';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ArrowLeft, MessageSquare, Users, FileText } from 'lucide-react';

export function AnalysisResults() {
  const { analysisResult, setAppState, setAnalysisResult } = useSessionStore();

  if (!analysisResult) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        No analysis results available
      </div>
    );
  }

  const handleNewAnalysis = () => {
    setAnalysisResult(null);
    setAppState('ready');
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Back button */}
      <Button
        variant="ghost"
        onClick={handleNewAnalysis}
        className="gap-2"
      >
        <ArrowLeft className="w-4 h-4" />
        New Analysis
      </Button>

      {/* Query info */}
      <div className="p-4 rounded-lg bg-card/50 border border-border">
        <p className="text-sm text-muted-foreground">Query</p>
        <p className="font-medium mt-1">{analysisResult.query}</p>
        <div className="flex items-center gap-4 mt-3 text-xs text-muted-foreground">
          <span>
            Classification: <span className="text-foreground">{analysisResult.query_classification.complexity}</span>
          </span>
          <span>
            Cost: <span className="text-foreground">{analysisResult.query_classification.estimated_cost}</span>
          </span>
          <span>
            Agents: <span className="text-foreground">{analysisResult.query_classification.selected_agents.length}</span>
          </span>
        </div>
      </div>

      {/* Verdict Card */}
      <VerdictCard verdict={analysisResult.final_verdict} />

      {/* Tabs for debate and individual responses */}
      <Tabs defaultValue="debate" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3 bg-muted/50">
          <TabsTrigger value="debate" className="gap-2">
            <MessageSquare className="w-4 h-4" />
            Debate
          </TabsTrigger>
          <TabsTrigger value="agents" className="gap-2">
            <Users className="w-4 h-4" />
            Agents
          </TabsTrigger>
          <TabsTrigger value="summary" className="gap-2">
            <FileText className="w-4 h-4" />
            Summary
          </TabsTrigger>
        </TabsList>

        <TabsContent value="debate" className="mt-4">
          <DebateLog debate={analysisResult.debate} />
        </TabsContent>

        <TabsContent value="agents" className="mt-4">
          <AgentResponses responses={analysisResult.individual_responses} />
        </TabsContent>

        <TabsContent value="summary" className="mt-4">
          <div className="p-6 rounded-lg bg-card border border-border">
            <pre className="text-sm text-foreground/90 whitespace-pre-wrap font-sans leading-relaxed">
              {analysisResult.final_verdict.summary}
            </pre>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
