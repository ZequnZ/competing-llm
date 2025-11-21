import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Send } from "lucide-react"

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled?: boolean;
}

export function ChatInput({ value, onChange, onSubmit, disabled }: ChatInputProps) {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className="flex gap-2">
      <Textarea
        placeholder="Type your prompt here... (Shift+Enter for new line)"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        className="min-h-[80px]"
        disabled={disabled}
      />
      <Button 
        size="icon" 
        className="h-auto w-16" 
        onClick={onSubmit}
        disabled={disabled || !value.trim()}
      >
        <Send className="h-6 w-6" />
      </Button>
    </div>
  );
}

