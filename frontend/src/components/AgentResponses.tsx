import { cn } from '@/lib/utils';
import type { IndividualResponse } from '@/types/api';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { BarChart3, Brain, Shield, TrendingUp } from 'lucide-react';

interface AgentResponsesProps {
  responses: IndividualResponse[];
}

const categoryIcons: Record<string, React.ElementType> = {
  analysts: BarChart3,
  researchers: Brain,
  managers: Shield,
  risk_analysts: Shield,
  trader: TrendingUp,
};

export function AgentResponses({ responses }: AgentResponsesProps) {
  if (!responses || responses.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No individual responses available
      </div>
    );
  }

  return (
    <Accordion type="single" collapsible className="space-y-2">
      {responses.map((response, idx) => {
        const Icon = categoryIcons[response.category] || Brain;

        return (
          <AccordionItem
            key={idx}
            value={`item-${idx}`}
            className="border border-border rounded-lg overflow-hidden bg-card/50"
          >
            <AccordionTrigger className="px-4 py-3 hover:bg-muted/50 [&[data-state=open]]:bg-muted/50">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-md bg-muted">
                  <Icon className="w-4 h-4 text-muted-foreground" />
                </div>
                <div className="text-left">
                  <span className="font-medium">{response.agent}</span>
                  <span className="text-xs text-muted-foreground ml-2 capitalize">
                    {response.category.replace('_', ' ')}
                  </span>
                </div>
              </div>
            </AccordionTrigger>
            <AccordionContent className="px-4 pb-4">
              <div className="space-y-3">
                {response.perspective && (
                  <p className="text-xs text-muted-foreground italic">
                    {response.perspective}
                  </p>
                )}
                <p className="text-sm text-foreground/90 leading-relaxed whitespace-pre-wrap">
                  {response.response}
                </p>
              </div>
            </AccordionContent>
          </AccordionItem>
        );
      })}
    </Accordion>
  );
}
