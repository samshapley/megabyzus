interface ToolOutputDisplayProps {
    output: any;
  }
  
  export default function ToolOutputDisplay({ output }: ToolOutputDisplayProps) {
    // Function to determine if the output is JSON
    const isJsonString = (str: string): boolean => {
      try {
        JSON.parse(str);
        return true;
      } catch (e) {
        return false;
      }
    };
  
    // Format the output based on its type
    const formatOutput = () => {
      if (!output) {
        return <p className="text-secondary-text">No output data available</p>;
      }
  
      // Handle string output
      if (typeof output === 'string') {
        // If it's a JSON string, try to format it
        if (isJsonString(output)) {
          try {
            const formattedJson = JSON.stringify(JSON.parse(output), null, 2);
            return (
              <pre className="font-mono text-sm overflow-x-auto p-1">
                {formattedJson}
              </pre>
            );
          } catch {
            // If JSON parsing fails, show as-is
            return <pre className="font-mono text-sm overflow-x-auto p-1">{output}</pre>;
          }
        }
        
        // Regular string
        return <p className="whitespace-pre-wrap">{output}</p>;
      }
  
      // Handle object output
      if (typeof output === 'object') {
        return (
          <pre className="font-mono text-sm overflow-x-auto p-1">
            {JSON.stringify(output, null, 2)}
          </pre>
        );
      }
  
      // Fallback for other types
      return <p className="whitespace-pre-wrap">{String(output)}</p>;
    };
  
    return (
      <div className="p-3 max-h-96 overflow-y-auto bg-black/20 rounded-sm">
        {formatOutput()}
      </div>
    );
  }
  