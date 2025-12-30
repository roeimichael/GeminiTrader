import { useState } from 'react';
import { useSessionStore } from '@/store/sessionStore';
import { useRunAnalysis } from '@/hooks/useApi';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Search, Calendar, Loader2 } from 'lucide-react';

export function AnalysisInput() {
  const { appState } = useSessionStore();
  const { mutate: runAnalysis, isPending } = useRunAnalysis();
  
  const [ticker, setTicker] = useState('');
  const [query, setQuery] = useState('');
  const [date, setDate] = useState('');

  const isDisabled = appState !== 'ready' || isPending;
  const canSubmit = ticker.trim() && query.trim() && !isPending;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;

    runAnalysis({
      ticker: ticker.toUpperCase().trim(),
      query: query.trim(),
      date: date || undefined,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Ticker input */}
        <div className="space-y-2">
          <Label htmlFor="ticker" className="text-sm font-medium">
            Stock Ticker
          </Label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              id="ticker"
              placeholder="AAPL"
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              disabled={isDisabled}
              className="pl-10 font-mono uppercase"
              maxLength={10}
            />
          </div>
        </div>

        {/* Date input (optional) */}
        <div className="space-y-2">
          <Label htmlFor="date" className="text-sm font-medium">
            Analysis Date <span className="text-muted-foreground">(optional)</span>
          </Label>
          <div className="relative">
            <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              id="date"
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              disabled={isDisabled}
              className="pl-10"
            />
          </div>
        </div>
      </div>

      {/* Query input */}
      <div className="space-y-2">
        <Label htmlFor="query" className="text-sm font-medium">
          Your Question
        </Label>
        <Textarea
          id="query"
          placeholder="What are your thoughts about investing in this stock?"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={isDisabled}
          rows={3}
          className="resize-none"
        />
      </div>

      {/* Submit button */}
      <Button
        type="submit"
        disabled={!canSubmit}
        size="lg"
        className="w-full gap-2"
      >
        {isPending ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Analyzing...
          </>
        ) : (
          <>
            <Search className="w-5 h-5" />
            Analyze Stock
          </>
        )}
      </Button>

      {appState !== 'ready' && appState !== 'analyzing' && (
        <p className="text-sm text-muted-foreground text-center">
          Initialize agents first to unlock analysis
        </p>
      )}
    </form>
  );
}
