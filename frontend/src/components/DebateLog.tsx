import { cn } from '@/lib/utils';
import type { DebateRound, DebateExchange } from '@/types/api';
import { MessageSquare, Gavel, TrendingUp, TrendingDown, Scale } from 'lucide-react';

interface DebateLogProps {
  debate: DebateRound[];
}

function getSpeakerStyle(speaker: string): {
  align: 'left' | 'right' | 'center';
  bgClass: string;
  borderClass: string;
  icon: React.ElementType;
  label: string;
} {
  const lowerSpeaker = speaker.toLowerCase();

  if (lowerSpeaker.includes('bull') || lowerSpeaker.includes('aggressive')) {
    return {
      align: 'left',
      bgClass: 'gradient-bullish',
      borderClass: 'border-bullish/30',
      icon: TrendingUp,
      label: 'Bullish',
    };
  }

  if (lowerSpeaker.includes('bear') || lowerSpeaker.includes('conservative')) {
    return {
      align: 'right',
      bgClass: 'gradient-bearish',
      borderClass: 'border-bearish/30',
      icon: TrendingDown,
      label: 'Bearish',
    };
  }

  if (lowerSpeaker.includes('judge') || lowerSpeaker.includes('manager')) {
    return {
      align: 'center',
      bgClass: 'bg-accent',
      borderClass: 'border-primary/30',
      icon: Gavel,
      label: 'Decision',
    };
  }

  if (lowerSpeaker.includes('neutral')) {
    return {
      align: 'center',
      bgClass: 'bg-neutral-muted',
      borderClass: 'border-neutral/30',
      icon: Scale,
      label: 'Neutral',
    };
  }

  if (lowerSpeaker.includes('trader')) {
    return {
      align: 'center',
      bgClass: 'bg-accent',
      borderClass: 'border-amber-500/30',
      icon: MessageSquare,
      label: 'Trade',
    };
  }

  return {
    align: 'left',
    bgClass: 'bg-muted',
    borderClass: 'border-border',
    icon: MessageSquare,
    label: '',
  };
}

function ExchangeBubble({ exchange }: { exchange: DebateExchange }) {
  const style = getSpeakerStyle(exchange.speaker);
  const Icon = style.icon;

  return (
    <div
      className={cn(
        'flex gap-3 animate-slide-up',
        style.align === 'right' && 'flex-row-reverse',
        style.align === 'center' && 'justify-center'
      )}
    >
      <div
        className={cn(
          'max-w-[85%] rounded-xl p-4 border',
          style.bgClass,
          style.borderClass,
          style.align === 'center' && 'max-w-full w-full'
        )}
      >
        {/* Speaker header */}
        <div className="flex items-center gap-2 mb-2">
          <div
            className={cn(
              'p-1.5 rounded-md',
              style.align === 'left' && 'bg-bullish/20',
              style.align === 'right' && 'bg-bearish/20',
              style.align === 'center' && 'bg-primary/20'
            )}
          >
            <Icon
              className={cn(
                'w-4 h-4',
                style.align === 'left' && 'text-bullish',
                style.align === 'right' && 'text-bearish',
                style.align === 'center' && 'text-primary'
              )}
            />
          </div>
          <span className="font-medium text-sm">{exchange.speaker}</span>
          {style.label && (
            <span
              className={cn(
                'text-xs px-2 py-0.5 rounded-full',
                style.align === 'left' && 'bg-bullish/20 text-bullish',
                style.align === 'right' && 'bg-bearish/20 text-bearish',
                style.align === 'center' && 'bg-primary/20 text-primary'
              )}
            >
              {style.label}
            </span>
          )}
        </div>

        {/* Statement */}
        <p className="text-sm text-foreground/90 leading-relaxed whitespace-pre-wrap">
          {exchange.statement}
        </p>
      </div>
    </div>
  );
}

export function DebateLog({ debate }: DebateLogProps) {
  if (!debate || debate.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No debate data available
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {debate.map((round) => (
        <div key={round.round} className="space-y-4">
          {/* Round header */}
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/20 text-primary font-mono text-sm font-bold">
              {round.round}
            </div>
            <div>
              <h4 className="font-semibold text-foreground">{round.topic}</h4>
              <p className="text-xs text-muted-foreground">
                {round.exchanges.length} exchange{round.exchanges.length !== 1 ? 's' : ''}
              </p>
            </div>
          </div>

          {/* Exchanges */}
          <div className="space-y-4 pl-4 border-l-2 border-border ml-4">
            {round.exchanges.map((exchange, idx) => (
              <ExchangeBubble key={idx} exchange={exchange} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
