'use client';

import { useRef, useEffect } from 'react';
import ChatInput from './ChatInput';

interface ResponsePanelProps {
  userRequest: string;
  userMessages: string[];
  responses: string[];
  onNewRequest: (request: string) => void;
  onReset: () => void;
  isLoading?: boolean;
  error?: string | null;
}

export default function ResponsePanel({ 
  userRequest, 
  userMessages,
  responses, 
  onNewRequest, 
  onReset,
  isLoading = false,
  error = null
}: ResponsePanelProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages are added or loading state changes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [responses, userMessages, isLoading, error]);

  return (
    <div className="flex flex-col h-full border-r border-white/10">
      {/* Header with Reset button */}
      <div className="py-3 px-4 border-b border-white/10 flex justify-between items-center">
        <div className="flex items-center">
          {isLoading && (
            <span className="text-xs px-2 py-1 bg-white/10 rounded-full">
              Processing...
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
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* User messages */}
        {userMessages.length > 0 ? (
          userMessages.map((message, index) => (
            <div key={`user-${index}`} className="animate-fade-in">
              <div className="font-semibold text-sm text-secondary-text mb-1">You</div>
              <div className="py-3 px-4 bg-secondary-background rounded-lg">
                {message}
              </div>
            </div>
          ))
        ) : userRequest ? (
          <div className="animate-fade-in">
            <div className="font-semibold text-sm text-secondary-text mb-1">You</div>
            <div className="py-3 px-4 bg-secondary-background rounded-lg">
              {userRequest}
            </div>
          </div>
        ) : null}
        
        {/* AI responses */}
        {responses.map((response, index) => (
          <div key={index} className="animate-fade-in">
            <div className="font-semibold text-sm text-secondary-text mb-1">Megabyzus</div>
            <div className="py-3 px-4 bg-secondary-background rounded-lg whitespace-pre-wrap">
              {response}
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
            <div className="py-3 px-4 bg-secondary-background rounded-lg flex items-center space-x-2">
              <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
              <div className="w-2 h-2 bg-white rounded-full animate-pulse delay-150"></div>
              <div className="w-2 h-2 bg-white rounded-full animate-pulse delay-300"></div>
              <span className="ml-2 text-sm text-secondary-text">Thinking...</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input container */}
      <div className="py-3 px-4 border-t border-white/10">
        <ChatInput
          onSubmit={onNewRequest}
          placeholder="Send a message..."
          disabled={isLoading}
        />
      </div>
    </div>
  );
}
