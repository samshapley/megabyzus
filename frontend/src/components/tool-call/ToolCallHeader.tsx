import { useState } from 'react';

interface ToolCallHeaderProps {
  toolName: string;
  isExpanded: boolean;
  onToggle: () => void;
}

export default function ToolCallHeader({ toolName, isExpanded, onToggle }: ToolCallHeaderProps) {
  return (
    <div 
      onClick={onToggle}
      className={`
        py-2 px-3 flex items-center justify-between 
        cursor-pointer hover:bg-white/5 transition-colors
        border-b border-white/10
        ${isExpanded ? 'bg-white/5' : 'bg-transparent'}
      `}
    >
      <div className="flex items-center space-x-2">
        <div className="w-5 h-5 flex items-center justify-center">
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            width="16" 
            height="16" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2" 
            strokeLinecap="round" 
            strokeLinejoin="round"
            className="text-[#B08D57]"
          >
            <path d="m22 2-7 20-4-9-9-4 20-7Z" />
          </svg>
        </div>
        <span className="text-sm font-medium text-[#B08D57]">
          {toolName}
        </span>
      </div>
      <div className="text-white/70">
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          width="16" 
          height="16" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2" 
          strokeLinecap="round" 
          strokeLinejoin="round"
          className={`transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}
        >
          <path d="m6 9 6 6 6-6" />
        </svg>
      </div>
    </div>
  );
}
