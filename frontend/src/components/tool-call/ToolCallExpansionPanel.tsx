import { useState } from 'react';
import { ToolCallData } from '@/types';
import ToolCallHeader from './ToolCallHeader';
import ToolCallTabs from './ToolCallTabs';

interface ToolCallExpansionPanelProps {
  toolCall: ToolCallData;
  isPending?: boolean; // New prop for pending tool calls
}

export default function ToolCallExpansionPanel({ 
  toolCall, 
  isPending = false 
}: ToolCallExpansionPanelProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className={`mt-2 mb-3 border ${isPending ? 'border-amber-500/30' : 'border-white/10'} 
                     rounded-lg overflow-hidden 
                     ${isPending ? 'bg-amber-900/10' : 'bg-secondary-background/50'} 
                     transition-all duration-200`}>
      <ToolCallHeader 
        toolName={toolCall.toolName} 
        isExpanded={isExpanded}
        onToggle={toggleExpanded}
        isPending={isPending}
      />
      
      {/* Collapsible Content */}
      {isExpanded && (
        <div className="animate-slideDown">
          <ToolCallTabs 
            inputs={toolCall.inputs} 
            output={isPending ? "Tool call in progress..." : toolCall.output}
            isPending={isPending}
          />
        </div>
      )}
      
      {/* Loading indicator for pending tool calls */}
      {isPending && (
        <div className="px-3 py-2 border-t border-amber-500/30 flex items-center text-sm text-amber-300">
          <div className="w-2 h-2 bg-amber-300 rounded-full animate-pulse mr-2"></div>
          <span>Processing tool call...</span>
        </div>
      )}
    </div>
  );
}