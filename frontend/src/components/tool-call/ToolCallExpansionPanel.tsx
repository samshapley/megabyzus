import { useState } from 'react';
import { ToolCallData } from '@/types';
import ToolCallHeader from './ToolCallHeader';
import ToolCallTabs from './ToolCallTabs';

interface ToolCallExpansionPanelProps {
  toolCall: ToolCallData;
}

export default function ToolCallExpansionPanel({ toolCall }: ToolCallExpansionPanelProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className="mt-2 mb-3 border border-white/10 rounded-lg overflow-hidden bg-secondary-background/50 transition-all duration-200">
      <ToolCallHeader 
        toolName={toolCall.toolName} 
        isExpanded={isExpanded}
        onToggle={toggleExpanded}
      />
      
      {/* Collapsible Content */}
      {isExpanded && (
        <div className="animate-slideDown">
          <ToolCallTabs 
            inputs={toolCall.inputs} 
            output={toolCall.output}
          />
        </div>
      )}
    </div>
  );
}
