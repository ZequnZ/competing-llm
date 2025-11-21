import type { LLMInfo } from '../api/client';
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"

interface LLMSelectorProps {
  llms: LLMInfo[];
  selectedIds: string[];
  onToggle: (id: string) => void;
}

export function LLMSelector({ llms, selectedIds, onToggle }: LLMSelectorProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {llms.map((llm) => (
        <div key={llm.llm_id} className="flex items-start space-x-3 p-4 border rounded-lg hover:bg-accent/50 transition-colors">
          <Checkbox 
            id={`llm-${llm.llm_id}`} 
            checked={selectedIds.includes(llm.llm_id)}
            onCheckedChange={() => onToggle(llm.llm_id)}
          />
          <div className="grid gap-1.5 leading-none">
            <div className="flex items-center gap-2">
              <Label 
                htmlFor={`llm-${llm.llm_id}`}
                className="font-semibold cursor-pointer"
              >
                {llm.name}
              </Label>
              {llm.reasoning_model && (
                <Badge variant="secondary" className="text-xs bg-purple-100 text-purple-800 hover:bg-purple-200">Reasoning</Badge>
              )}
              <Badge variant="secondary" className="text-xs">{llm.speed_rating}</Badge>
              <Badge variant="outline" className="text-xs">{llm.provider}</Badge>
            </div>
            <p className="text-sm text-muted-foreground">
              {llm.description}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
