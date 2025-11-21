import type { ChatResponse, LLMInfo } from '../api/client';
import { ResponseCard } from './ResponseCard';

interface ResponseGridProps {
  selectedLLMs: LLMInfo[];
  responses: Record<string, ChatResponse>;
  loadingStates: Record<string, boolean>;
}

export function ResponseGrid({ selectedLLMs, responses, loadingStates }: ResponseGridProps) {
  if (selectedLLMs.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 border-2 border-dashed rounded-lg text-muted-foreground">
        Select models above to see their responses here
      </div>
    );
  }

  return (
    <div className={`grid gap-4 ${
      selectedLLMs.length === 1 ? 'grid-cols-1' : 
      selectedLLMs.length === 2 ? 'grid-cols-1 md:grid-cols-2' :
      'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
    }`}>
      {selectedLLMs.map((llm) => {
        const response = responses[llm.llm_id];
        const isLoading = loadingStates[llm.llm_id] || false;
        
        return (
          <ResponseCard 
            key={llm.llm_id}
            modelName={llm.name}
            content={response?.error ? `Error: ${response.error}` : (response?.content || '')}
            timestamp={response?.timestamp}
            loading={isLoading}
          />
        );
      })}
    </div>
  );
}
