import { cn } from '@/lib/utils';
import { useAgents } from '@/hooks/useApi';
import { useSessionStore } from '@/store/sessionStore';
import { AgentCard } from './AgentCard';
import { Skeleton } from '@/components/ui/skeleton';
import type { AgentInfo } from '@/types/api';

const categoryLabels: Record<string, string> = {
  analysts: 'Analysts',
  researchers: 'Researchers',
  managers: 'Managers',
  risk_analysts: 'Risk Analysts',
  trader: 'Trader',
};

export function AgentSelector() {
  const { data: agents, isLoading, error } = useAgents();
  const { selectedAgents, toggleAgent } = useSessionStore();

  if (isLoading) {
    return (
      <div className="space-y-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="space-y-3">
            <Skeleton className="h-5 w-24" />
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {[1, 2, 3].map((j) => (
                <Skeleton key={j} className="h-28" />
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 rounded-lg border border-destructive/50 bg-destructive/10 text-center">
        <p className="text-destructive font-medium">Failed to load agents</p>
        <p className="text-sm text-muted-foreground mt-1">
          Make sure the API server is running at localhost:8000
        </p>
      </div>
    );
  }

  if (!agents) return null;

  // Flatten and group agents by category
  const allAgents: { key: string; agent: AgentInfo; category: string }[] = [];
  
  Object.entries(agents).forEach(([category, categoryAgents]) => {
    Object.entries(categoryAgents).forEach(([key, agent]) => {
      const agentKey = `${key}_${category === 'trader' ? '' : category.slice(0, -1)}`.replace(/_$/, '');
      // Map to proper API keys
      const apiKey = key + (category !== 'trader' ? '_' + category.slice(0, -1).replace('s', '') : '');
      allAgents.push({
        key: `${key}_${category}`,
        agent: agent as AgentInfo,
        category,
      });
    });
  });

  // Group by category
  const grouped = allAgents.reduce((acc, item) => {
    if (!acc[item.category]) acc[item.category] = [];
    acc[item.category].push(item);
    return acc;
  }, {} as Record<string, typeof allAgents>);

  // Create proper API agent keys
  const getAgentApiKey = (key: string, category: string): string => {
    const categoryMap: Record<string, string> = {
      analysts: 'analyst',
      researchers: 'researcher',
      managers: 'manager',
      risk_analysts: 'analyst',
      trader: '',
    };
    const suffix = categoryMap[category];
    return suffix ? `${key}_${suffix}` : key;
  };

  return (
    <div className="space-y-6">
      {Object.entries(grouped).map(([category, categoryAgents]) => (
        <div key={category} className="space-y-3">
          <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
            {categoryLabels[category] || category}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
            {categoryAgents.map(({ key, agent, category: cat }) => {
              const apiKey = getAgentApiKey(key.split('_')[0], cat);
              return (
                <AgentCard
                  key={key}
                  agentKey={apiKey}
                  agent={agent}
                  isSelected={selectedAgents.includes(apiKey)}
                  onToggle={() => toggleAgent(apiKey)}
                />
              );
            })}
          </div>
        </div>
      ))}

      {selectedAgents.length > 0 && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground pt-2">
          <span className="font-mono text-primary">{selectedAgents.length}</span>
          <span>agent{selectedAgents.length !== 1 ? 's' : ''} selected</span>
        </div>
      )}
    </div>
  );
}
