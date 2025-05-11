import { useState } from 'react';
import InputParamsTable from './InputParamsTable';
import ToolOutputDisplay from './ToolOutputDisplay';
import { ToolCallTab } from '@/types';

interface ToolCallTabsProps {
  inputs: Record<string, any>;
  output: any;
  isPending?: boolean; // New prop to indicate pending state
}

export default function ToolCallTabs({ 
  inputs, 
  output,
  isPending = false 
}: ToolCallTabsProps) {
  const [activeTab, setActiveTab] = useState<ToolCallTab>('input');

  return (
    <div className={`${isPending ? 'bg-amber-900/10' : 'bg-secondary-background'} rounded-b-lg overflow-hidden`}>
      {/* Tab Navigation */}
      <div className={`flex border-b ${isPending ? 'border-amber-500/30' : 'border-white/10'}`}>
        <button
          className={`py-2 px-4 text-sm font-medium transition-colors ${
            activeTab === 'input'
              ? isPending 
                ? 'text-amber-300 border-b-2 border-amber-500'
                : 'text-white border-b-2 border-[#B08D57]'
              : 'text-secondary-text hover:text-white hover:bg-white/5'
          }`}
          onClick={() => setActiveTab('input')}
        >
          Input
        </button>
        <button
          className={`py-2 px-4 text-sm font-medium transition-colors ${
            activeTab === 'output'
              ? isPending 
                ? 'text-amber-300 border-b-2 border-amber-500'
                : 'text-white border-b-2 border-[#B08D57]'
              : 'text-secondary-text hover:text-white hover:bg-white/5'
          }`}
          onClick={() => setActiveTab('output')}
          disabled={isPending} // Disable output tab when pending
        >
          Output
          {isPending && ' (pending)'}
        </button>
      </div>

      {/* Tab Content */}
      <div className="transition-all duration-200">
        {activeTab === 'input' ? (
          <InputParamsTable inputs={inputs} isPending={isPending} />
        ) : (
          <div className="p-3">
            {isPending ? (
              <div className="flex items-center justify-center p-4 text-amber-300">
                <div className="w-2 h-2 bg-amber-300 rounded-full animate-pulse mr-2"></div>
                <span>Waiting for tool results...</span>
              </div>
            ) : (
              <ToolOutputDisplay output={output} />
            )}
          </div>
        )}
      </div>
    </div>
  );
}