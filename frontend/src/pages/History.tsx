import { AppLayout } from '@/components/AppLayout';
import { useHistory, useClearHistory } from '@/hooks/useApi';
import { useSessionStore } from '@/store/sessionStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Trash2, Clock, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';

const History = () => {
  const { sessionId } = useSessionStore();
  const { data: history, isLoading } = useHistory();
  const { mutate: clearHistory, isPending: isClearing } = useClearHistory();

  const getRecommendationIcon = (rec: string) => {
    const r = rec?.toUpperCase();
    if (r === 'BUY') return <TrendingUp className="w-4 h-4 text-bullish" />;
    if (r === 'SELL') return <TrendingDown className="w-4 h-4 text-bearish" />;
    return <Minus className="w-4 h-4 text-neutral-signal" />;
  };

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Analysis History</h1>
            <p className="text-muted-foreground">
              View your past stock analyses
            </p>
          </div>
          {history && history.length > 0 && (
            <Button
              variant="outline"
              onClick={() => clearHistory()}
              disabled={isClearing}
              className="gap-2 text-destructive hover:text-destructive"
            >
              <Trash2 className="w-4 h-4" />
              Clear History
            </Button>
          )}
        </div>

        {!sessionId && (
          <Card className="gradient-card border-border/50">
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground">
                Start a session to view analysis history
              </p>
            </CardContent>
          </Card>
        )}

        {sessionId && isLoading && (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-24" />
            ))}
          </div>
        )}

        {sessionId && !isLoading && (!history || history.length === 0) && (
          <Card className="gradient-card border-border/50">
            <CardContent className="py-12 text-center">
              <Clock className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">
                No analysis history yet. Run your first analysis!
              </p>
            </CardContent>
          </Card>
        )}

        {history && history.length > 0 && (
          <div className="space-y-3">
            {history.map((entry) => (
              <Card key={entry.id} className="gradient-card border-border/50 hover:border-border transition-colors">
                <CardContent className="py-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      {getRecommendationIcon(entry.recommendation)}
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold">{entry.ticker}</span>
                          <span
                            className={cn(
                              'text-xs px-2 py-0.5 rounded-full',
                              entry.recommendation?.toUpperCase() === 'BUY' && 'bg-bullish/20 text-bullish',
                              entry.recommendation?.toUpperCase() === 'SELL' && 'bg-bearish/20 text-bearish',
                              entry.recommendation?.toUpperCase() === 'HOLD' && 'bg-neutral-muted text-neutral-signal'
                            )}
                          >
                            {entry.recommendation}
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground line-clamp-1 mt-1">
                          {entry.query}
                        </p>
                      </div>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {new Date(entry.timestamp).toLocaleString()}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
};

export default History;
