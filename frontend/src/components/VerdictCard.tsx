import { cn } from '@/lib/utils';
import type { FinalVerdict as FinalVerdictType } from '@/types/api';
import { TrendingUp, TrendingDown, Minus, Target, Shield, Calendar, Clock } from 'lucide-react';

interface VerdictCardProps {
  verdict: FinalVerdictType;
}

function getRecommendationStyle(recommendation: string) {
  const rec = recommendation.toUpperCase();
  
  if (rec === 'BUY') {
    return {
      bgClass: 'gradient-bullish border-bullish/50',
      textClass: 'text-bullish',
      icon: TrendingUp,
      label: 'BUY',
    };
  }
  
  if (rec === 'SELL') {
    return {
      bgClass: 'gradient-bearish border-bearish/50',
      textClass: 'text-bearish',
      icon: TrendingDown,
      label: 'SELL',
    };
  }
  
  return {
    bgClass: 'bg-neutral-muted border-neutral/50',
    textClass: 'text-neutral-signal',
    icon: Minus,
    label: 'HOLD',
  };
}

export function VerdictCard({ verdict }: VerdictCardProps) {
  const style = getRecommendationStyle(verdict.overall_recommendation);
  const Icon = style.icon;

  const sentimentTotal =
    verdict.sentiment_breakdown.bullish +
    verdict.sentiment_breakdown.bearish +
    verdict.sentiment_breakdown.neutral;

  return (
    <div className={cn('rounded-xl border-2 p-6 space-y-6', style.bgClass)}>
      {/* Header with ticker and date */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-3xl font-bold tracking-tight">
              {verdict.ticker}
            </span>
            <span
              className={cn(
                'px-3 py-1 rounded-full text-sm font-semibold',
                style.textClass,
                'bg-background/50'
              )}
            >
              {verdict.confidence_level}
            </span>
          </div>
          <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
            <span className="flex items-center gap-1.5">
              <Calendar className="w-4 h-4" />
              {verdict.trade_date}
            </span>
            <span className="flex items-center gap-1.5">
              <Clock className="w-4 h-4" />
              {new Date(verdict.timestamp).toLocaleTimeString()}
            </span>
          </div>
        </div>
      </div>

      {/* Main recommendation */}
      <div className="flex items-center gap-4">
        <div
          className={cn(
            'p-4 rounded-xl bg-background/30',
            style.textClass
          )}
        >
          <Icon className="w-10 h-10" />
        </div>
        <div>
          <div className={cn('text-5xl font-bold tracking-tight', style.textClass)}>
            {style.label}
          </div>
          <p className="text-muted-foreground text-sm mt-1">Overall Recommendation</p>
        </div>
      </div>

      {/* Sentiment breakdown */}
      <div className="space-y-3">
        <h4 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
          <Target className="w-4 h-4" />
          Sentiment Breakdown
        </h4>
        <div className="flex gap-2 h-3 rounded-full overflow-hidden bg-background/30">
          {verdict.sentiment_breakdown.bullish > 0 && (
            <div
              className="bg-bullish transition-all"
              style={{
                width: `${(verdict.sentiment_breakdown.bullish / sentimentTotal) * 100}%`,
              }}
            />
          )}
          {verdict.sentiment_breakdown.neutral > 0 && (
            <div
              className="bg-neutral transition-all"
              style={{
                width: `${(verdict.sentiment_breakdown.neutral / sentimentTotal) * 100}%`,
              }}
            />
          )}
          {verdict.sentiment_breakdown.bearish > 0 && (
            <div
              className="bg-bearish transition-all"
              style={{
                width: `${(verdict.sentiment_breakdown.bearish / sentimentTotal) * 100}%`,
              }}
            />
          )}
        </div>
        <div className="flex justify-between text-xs">
          <span className="text-bullish">
            Bullish: {verdict.sentiment_breakdown.bullish} ({verdict.sentiment_breakdown.bullish_percentage.toFixed(0)}%)
          </span>
          <span className="text-neutral-signal">
            Neutral: {verdict.sentiment_breakdown.neutral}
          </span>
          <span className="text-bearish">
            Bearish: {verdict.sentiment_breakdown.bearish}
          </span>
        </div>
      </div>

      {/* Trade decision */}
      <div className="space-y-2">
        <h4 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
          <Shield className="w-4 h-4" />
          Trade Decision
        </h4>
        <p className="text-sm text-foreground/90 leading-relaxed">
          {verdict.final_trade_decision}
        </p>
      </div>

      {/* Investment plan */}
      {verdict.investment_plan && (
        <div className="p-4 rounded-lg bg-background/30 font-mono text-sm">
          <h4 className="text-xs font-medium text-muted-foreground mb-2 uppercase tracking-wider">
            Investment Plan
          </h4>
          <p className="text-foreground/90 whitespace-pre-wrap">
            {verdict.investment_plan}
          </p>
        </div>
      )}
    </div>
  );
}
