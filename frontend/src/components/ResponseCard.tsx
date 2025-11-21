import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface ResponseCardProps {
  modelName: string;
  content: string;
  timestamp?: string;
  loading?: boolean;
}

export function ResponseCard({ modelName, content, timestamp, loading }: ResponseCardProps) {
  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex justify-between items-center">
          <CardTitle className="text-lg font-medium">{modelName}</CardTitle>
          {timestamp && <span className="text-xs text-muted-foreground">{new Date(timestamp).toLocaleTimeString()}</span>}
        </div>
      </CardHeader>
      <CardContent className="flex-1">
        {loading ? (
           <div className="flex items-center justify-center h-full py-8 text-muted-foreground animate-pulse">
             Generating response...
           </div>
        ) : (
          <div className="whitespace-pre-wrap text-sm leading-relaxed">
            {content || <span className="text-muted-foreground italic">Waiting for response...</span>}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

