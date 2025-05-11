'use client';

import { useRef, useEffect } from 'react';
import ChatInput from './ChatInput';
import ToolCallExpansionPanel from '../tool-call/ToolCallExpansionPanel';
import { Message, ToolCallData } from '@/types';

interface ResponsePanelProps {
  userRequest: string;
  messages: Message[];
  onNewRequest: (request: string) => void;
  onReset: () => void;
  isLoading?: boolean;
  processingTools?: boolean;  // New prop for tool processing state
  error?: string | null;
}

export default function ResponsePanel({ 
  userRequest, 
  messages,
  onNewRequest, 
  onReset,
  isLoading = false,
  processingTools = false,  // Default to false
  error = null
}: ResponsePanelProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages are added or loading state changes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading, processingTools, error]);

  return (
<div className="flex flex-col h-full border-r border-white/10 max-h-screen">
      {/* Header with Reset button */}
<div className="py-3 px-4 border-b border-white/10 flex justify-between items-center flex-shrink-0">
        <div className="flex items-center">
          <h2 className="font-semibold mr-3">Conversation</h2>
          {isLoading && (
            <span className="text-xs px-2 py-1 bg-white/10 rounded-full">
              Processing...
            </span>
          )}
          {processingTools && (
            <span className="text-xs px-2 py-1 bg-amber-800/50 text-amber-200 rounded-full ml-2">
              Using tools...
            </span>
          )}
        </div>
        <button
          onClick={onReset}
          className="text-sm px-3 py-1 rounded-full border border-white/20 hover:bg-white/10 transition-colors"
        >
          New Chat
        </button>
      </div>
      
      {/* Messages container */}
<div className="flex-1 overflow-y-auto p-4 space-y-6 h-0 min-h-0">
        {/* Render messages in chronological order */}
        {messages.map((message) => (
          <div 
            key={message.id} 
            className={`animate-fade-in ${message.sender === 'user' ? 'flex justify-end' : ''}`}
          >
            <div className={`max-w-[80%] ${message.sender === 'user' ? 'ml-auto' : ''}`}>
              <div className={`font-semibold text-sm text-secondary-text mb-1 ${message.sender === 'user' ? 'text-right' : ''}`}>
                {message.sender === 'user' ? 'You' : 'Megabyzus'}
              </div>
              <div 
                className={`py-3 px-4 rounded-lg ${
                  message.sender === 'user' 
                    ? 'bg-primary-background rounded-tr-none' 
                    : 'bg-secondary-background rounded-tl-none'
                } ${message.sender === 'agent' ? 'whitespace-pre-wrap' : ''}`}
              >
                {message.content}
                
                {/* Show "Using tools..." indicator for messages with toolCallsPending */}
                {message.sender === 'agent' && message.toolCallsPending && (
                  <div className="mt-2 text-sm text-amber-300 flex items-center">
                    <div className="w-2 h-2 bg-amber-300 rounded-full animate-pulse mr-2"></div>
                    <span>Using tools to find information...</span>
                  </div>
                )}
              </div>
              
              {/* Tool Call Expansion Panels */}
              {message.sender === 'agent' && message.toolCalls && message.toolCalls.length > 0 && (
                <div className="mt-1">
                  {message.toolCalls.map((toolCall) => (
                    <ToolCallExpansionPanel
                      key={toolCall.id}
                      toolCall={toolCall}
                      isPending={toolCall.stage === 'pending'}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        
        {/* Error message */}
        {error && (
          <div className="animate-fade-in">
            <div className="font-semibold text-sm text-red-400 mb-1">Error</div>
            <div className="py-3 px-4 bg-red-900/30 border border-red-700/50 rounded-lg text-red-200">
              {error}
              <div className="mt-2 text-sm">
                <button
                  onClick={onReset}
                  className="text-red-300 hover:text-red-100 underline"
                >
                  Start a new conversation
                </button>
              </div>
            </div>
          </div>
        )}
        
        {/* Loading indicator shown when waiting for a response */}
        {isLoading && (
          <div className="animate-fade-in">
            <div className="font-semibold text-sm text-secondary-text mb-1">Megabyzus</div>
            <div className="py-3 px-4 bg-secondary-background rounded-lg flex items-center space-x-2 rounded-tl-none">
              <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
              <div className="w-2 h-2 bg-white rounded-full animate-pulse delay-150"></div>
              <div className="w-2 h-2 bg-white rounded-full animate-pulse delay-300"></div>
              <span className="ml-2 text-sm text-secondary-text">Thinking...</span>
            </div>
          </div>
        )}
        
        {/* Tool Processing indicator shown when processing tools */}
        {!isLoading && processingTools && (
          <div className="animate-fade-in">
            <div className="font-semibold text-sm text-secondary-text mb-1">Megabyzus</div>
            <div className="py-3 px-4 bg-secondary-background rounded-lg flex items-center space-x-2 rounded-tl-none">
              <div className="w-2 h-2 bg-amber-300 rounded-full animate-pulse"></div>
              <div className="w-2 h-2 bg-amber-300 rounded-full animate-pulse delay-150"></div>
              <div className="w-2 h-2 bg-amber-300 rounded-full animate-pulse delay-300"></div>
              <span className="ml-2 text-sm text-amber-300">Using tools to search...</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input container */}
<div className="py-3 px-4 border-t border-white/10 flex-shrink-0">
        <ChatInput
          onSubmit={onNewRequest}
          placeholder="Send a message..."
          disabled={isLoading || processingTools}
        />
      </div>
    </div>
  );
}