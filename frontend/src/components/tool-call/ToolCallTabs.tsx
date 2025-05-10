import { useState } from 'react';
import InputParamsTable from './InputParamsTable';
import ToolOutputDisplay from './ToolOutputDisplay';
import { ToolCallTab } from '@/types';

interface ToolCallTabsProps {
  inputs: Record<string, any>;
  output: any;
}

export default function ToolCallTabs({ inputs, output }: ToolCallTabsProps) {
  const [activeTab, setActiveTab] = useState<ToolCallTab>('input');

  return (
    <div className="bg-secondary-background rounded-b-lg overflow-hidden">
      {/* Tab Navigation */}
      <div className="flex border-b border-white/10">
        <button
          className={`py-2 px-4 text-sm font-medium transition-colors ${
            activeTab === 'input'
              ? 'text-white border-b-2 border-[#B08D57]'
              : 'text-secondary-text hover:text-white hover:bg-white/5'
          }`}
          onClick={() => setActiveTab('input')}
        >
          Input
        </button>
        <button
          className={`py-2 px-4 text-sm font-medium transition-colors ${
            activeTab === 'output'
              ? 'text-white border-b-2 border-[#B08D57]'
              : 'text-secondary-text hover:text-white hover:bg-white/5'
          }`}
          onClick={() => setActiveTab('output')}
        >
          Output
        </button>
      </div>

      {/* Tab Content */}
      <div className="transition-all duration-200">
        {activeTab === 'input' ? (
          <InputParamsTable inputs={inputs} />
        ) : (
          <div className="p-3">
            <ToolOutputDisplay output={output} />
          </div>
        )}
      </div>
    </div>
  );
}
