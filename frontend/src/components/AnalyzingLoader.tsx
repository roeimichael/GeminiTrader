import { cn } from '@/lib/utils';

interface AnalyzingLoaderProps {
  ticker?: string;
}

const loadingMessages = [
  'Gathering market data...',
  'Analyzing technical indicators...',
  'Processing fundamentals...',
  'Scanning news sentiment...',
  'Running bull/bear debate...',
  'Assessing risk factors...',
  'Compiling final verdict...',
];

export function AnalyzingLoader({ ticker }: AnalyzingLoaderProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 space-y-8">
      {/* Animated logo/spinner */}
      <div className="relative">
        <div className="w-24 h-24 rounded-full border-4 border-muted animate-pulse" />
        <div className="absolute inset-0 w-24 h-24 rounded-full border-4 border-primary border-t-transparent animate-spin" />
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="font-mono text-lg font-bold text-primary">
            {ticker || 'AI'}
          </span>
        </div>
      </div>

      {/* Loading text */}
      <div className="text-center space-y-2">
        <h3 className="text-xl font-semibold">Analyzing {ticker || 'Stock'}</h3>
        <p className="text-muted-foreground">
          Multi-agent analysis in progress...
        </p>
      </div>

      {/* Terminal-style log */}
      <div className="w-full max-w-md p-4 rounded-lg bg-card border border-border font-mono text-sm space-y-1 overflow-hidden">
        {loadingMessages.map((msg, idx) => (
          <div
            key={idx}
            className={cn(
              'flex items-center gap-2 transition-opacity',
              'animate-fade-in'
            )}
            style={{ animationDelay: `${idx * 0.3}s` }}
          >
            <span className="text-primary">▸</span>
            <span className="text-muted-foreground">{msg}</span>
          </div>
        ))}
        <div className="flex items-center gap-2 animate-pulse">
          <span className="text-primary">▸</span>
          <span className="text-foreground">Processing</span>
          <span className="inline-flex">
            <span className="animate-bounce" style={{ animationDelay: '0s' }}>.</span>
            <span className="animate-bounce" style={{ animationDelay: '0.1s' }}>.</span>
            <span className="animate-bounce" style={{ animationDelay: '0.2s' }}>.</span>
          </span>
        </div>
      </div>

      <p className="text-xs text-muted-foreground">
        This may take 30-60 seconds
      </p>
    </div>
  );
}
