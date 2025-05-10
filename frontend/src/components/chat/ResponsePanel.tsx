'use client';

import { useRef, useEffect } from 'react';
import ChatInput from './ChatInput';

interface ResponsePanelProps {
  userRequest: string;
  responses: string[];
  onNewRequest: (request: string) => void;
  onReset: () => void;
}

export default function ResponsePanel({ 
  userRequest, 
  responses, 
  onNewRequest, 
  onReset 
}: ResponsePanelProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages are added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [responses]);

  return (
    <div className="flex flex-col h-full border-r border-white/10">
      {/* Header with Reset button */}
      <div className="py-3 px-4 border-b border-white/10 flex justify-between items-center">
        <h2 className="font-semibold">Conversation</h2>
        <button
          onClick={onReset}
          className="text-sm px-3 py-1 rounded-full border border-white/20 hover:bg-white/10 transition-colors"
        >
          New Chat
        </button>
      </div>
      
      {/* Messages container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* User message */}
        <div className="animate-fade-in">
          <div className="font-semibold text-sm text-secondary-text mb-1">You</div>
          <div className="py-3 px-4 bg-secondary-background rounded-lg">
            {userRequest}
          </div>
        </div>
        
        {/* AI responses */}
        {responses.map((response, index) => (
          <div key={index} className="animate-fade-in">
            <div className="font-semibold text-sm text-secondary-text mb-1">Megabyzus</div>
            <div className="py-3 px-4 bg-secondary-background rounded-lg">
              {response}
            </div>
          </div>
        ))}
        
        {/* Loading indicator shown when waiting for a response */}
        {responses.length < 1 && (
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
        />
      </div>
    </div>
  );
}