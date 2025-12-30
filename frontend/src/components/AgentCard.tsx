import { cn } from '@/lib/utils';
import type { AgentInfo } from '@/types/api';
import { Check, Brain, TrendingUp, TrendingDown, Shield, BarChart3 } from 'lucide-react';

interface AgentCardProps {
  agentKey: string;
  agent: AgentInfo;
  isSelected: boolean;
  onToggle: () => void;
}

const categoryIcons: Record<string, React.ElementType> = {
  analysts: BarChart3,
  researchers: Brain,
  managers: Shield,
  risk_analysts: TrendingDown,
  trader: TrendingUp,
};

const categoryColors: Record<string, string> = {
  analysts: 'border-blue-500/30 hover:border-blue-500/50',
  researchers: 'border-purple-500/30 hover:border-purple-500/50',
  managers: 'border-amber-500/30 hover:border-amber-500/50',
  risk_analysts: 'border-rose-500/30 hover:border-rose-500/50',
  trader: 'border-emerald-500/30 hover:border-emerald-500/50',
};

export function AgentCard({ agentKey, agent, isSelected, onToggle }: AgentCardProps) {
  const Icon = categoryIcons[agent.category] || Brain;
  const colorClass = categoryColors[agent.category] || 'border-muted';

  return (
    <button
      onClick={onToggle}
      className={cn(
        'relative p-4 rounded-lg border-2 transition-all duration-200 text-left group',
        'bg-card/50 hover:bg-card',
        colorClass,
        isSelected && 'border-primary bg-primary/5 shadow-glow'
      )}
    >
      {/* Selection indicator */}
      <div
        className={cn(
          'absolute top-3 right-3 w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all',
          isSelected
            ? 'bg-primary border-primary'
            : 'border-muted-foreground/30 group-hover:border-muted-foreground/50'
        )}
      >
        {isSelected && <Check className="w-3 h-3 text-primary-foreground" />}
      </div>

      {/* Icon and name */}
      <div className="flex items-start gap-3">
        <div
          className={cn(
            'p-2 rounded-md transition-colors',
            isSelected ? 'bg-primary/20' : 'bg-muted'
          )}
        >
          <Icon
            className={cn(
              'w-5 h-5 transition-colors',
              isSelected ? 'text-primary' : 'text-muted-foreground'
            )}
          />
        </div>
        <div className="flex-1 min-w-0 pr-6">
          <h3 className="font-medium text-foreground truncate">{agent.name}</h3>
          <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
            {agent.description}
          </p>
        </div>
      </div>

      {/* Memory indicator */}
      {agent.requires_memory && (
        <div className="mt-3 flex items-center gap-1.5 text-xs text-muted-foreground">
          <div className="w-1.5 h-1.5 rounded-full bg-amber-500" />
          <span>Requires memory</span>
        </div>
      )}
    </button>
  );
}
