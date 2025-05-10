'use client';

import { useState, useRef, useEffect } from 'react';

interface ChatInputProps {
  onSubmit: (value: string) => void;
  placeholder?: string;
  initialValue?: string;
  autoFocus?: boolean;
  disabled?: boolean;
}

export default function ChatInput({ 
  onSubmit, 
  placeholder = 'Type your message...',
  initialValue = '',
  autoFocus = false,
  disabled = false
}: ChatInputProps) {
  const [inputValue, setInputValue] = useState(initialValue);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  
  // Auto-resize textarea as content grows
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${inputRef.current.scrollHeight}px`;
    }
  }, [inputValue]);
  
  // Set focus on input if autoFocus is true
  useEffect(() => {
    if (autoFocus && inputRef.current && !disabled) {
      inputRef.current.focus();
    }
  }, [autoFocus, disabled]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    
    if (inputValue.trim() && !disabled) {
      onSubmit(inputValue.trim());
      setInputValue('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && !disabled) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <form 
      onSubmit={handleSubmit} 
      className="relative w-full transition-all duration-200 ease-in-out"
    >
      <div className="relative flex items-center">
        <textarea
          ref={inputRef}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={disabled ? 'Agent API is unavailable...' : placeholder}
          rows={1}
          disabled={disabled}
          className={`w-full py-3 px-4 pr-16 bg-secondary-background text-white rounded-3xl resize-none max-h-32 overflow-y-auto border border-transparent 
            ${disabled ? 'opacity-50 cursor-not-allowed' : 'focus:outline-none focus:border-[#B08D57] focus:ring-2 focus:ring-[#B08D57]/50 hover:border-[#B08D57]/30 hover:ring-1 hover:ring-[#B08D57]/30'} 
            transition-all duration-200`}
          style={{ minHeight: '56px' }}
        />
        <button
          type="submit"
          disabled={!inputValue.trim() || disabled}
          className={`absolute right-3 p-2 rounded-md ${
            inputValue.trim() && !disabled
              ? 'text-white hover:bg-white/10' 
              : 'text-gray-500 cursor-not-allowed'
          } transition-colors`}
          aria-label="Send message"
        >
          <img 
            src="/sword.svg" 
            width="20" 
            height="20" 
            alt="Send message"
            className={`w-5 h-5 ${disabled ? 'opacity-50' : ''}`}
          />
        </button>
      </div>
    </form>
  );
}
