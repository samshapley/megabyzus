'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import ChatInput from '@/components/chat/ChatInput';
import ResponsePanel from '@/components/chat/ResponsePanel';
import DisplayPanel from '@/components/display/DisplayPanel';
import RootLayout from '@/components/layout/RootLayout';

export default function Home() {
  // State to track whether a request has been sent
  const [requestSent, setRequestSent] = useState(false);
  // State to store the current user input/request
  const [userRequest, setUserRequest] = useState('');
  // State for AI responses (this would typically come from an API)
  const [aiResponses, setAiResponses] = useState<string[]>([]);
  // State for display panel content (placeholder for now)
  const [displayItems, setDisplayItems] = useState<any[]>([]);
  // State to track if we're on the client side
  const [isMounted, setIsMounted] = useState(false);

  // This useEffect will only run on the client after hydration
  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Handler for when a request is submitted
  const handleRequestSubmit = (request: string) => {
    setUserRequest(request);
    setRequestSent(true);
    
    // Simulate an AI response (in a real app, this would be an API call)
    setTimeout(() => {
      setAiResponses([
        ...aiResponses,
        `This is a simulated response to: "${request}"`
      ]);
    }, 1000);
  };

  // Handler for starting a new conversation
  const handleReset = () => {
    setRequestSent(false);
    setUserRequest('');
    setAiResponses([]);
    setDisplayItems([]);
  };

  // If we're not mounted yet, render nothing to prevent hydration mismatch
  if (!isMounted) {
    return <div className="min-h-screen bg-black"></div>;
  }

  return (
    <RootLayout>
      {!requestSent ? (
        // Initial state: centered input
        <div className="flex flex-col items-center justify-center h-full min-h-screen">
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full max-w-3xl px-6 flex flex-col items-center animate-fade-in">
            <div className="mb-16">
              <Image 
                src="/logo.png" 
                alt="Megabyzus Logo" 
                width={161} 
                height={161}
                priority 
              />
            </div>
            {/* Heading removed as requested */}
            <div className="w-full">
              <ChatInput 
                onSubmit={handleRequestSubmit} 
                placeholder=""
                autoFocus
              />
            </div>
          </div>
        </div>
      ) : (
        // Dual panel layout after a request is sent
        <div className="panel-layout">
          {/* Left panel for AI responses */}
          <ResponsePanel 
            userRequest={userRequest} 
            responses={aiResponses} 
            onNewRequest={handleRequestSubmit} 
            onReset={handleReset} 
          />
          
          {/* Right panel for displaying artifacts */}
          <DisplayPanel 
            items={displayItems} 
          />
        </div>
      )}
    </RootLayout>
  );
}