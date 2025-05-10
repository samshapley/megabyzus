'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import ChatInput from '@/components/chat/ChatInput';
import ResponsePanel from '@/components/chat/ResponsePanel';
import DisplayPanel from '@/components/display/DisplayPanel';
import RootLayout from '@/components/layout/RootLayout';
import AgentApi from '@/services/api';
import { Message, ToolCallData } from '@/types';

export default function Home() {
  // State to track whether a request has been sent
  const [requestSent, setRequestSent] = useState(false);
  // State to store the current user input/request
  const [userRequest, setUserRequest] = useState('');

  // Unified state for all messages in chronological order
  const [messages, setMessages] = useState<Message[]>([]);
  // State for display panel content (placeholder for now)
  const [displayItems, setDisplayItems] = useState<any[]>([]);
  // State to track if we're on the client side
  const [isMounted, setIsMounted] = useState(false);
  // State to store the session ID for the conversation
  const [sessionId, setSessionId] = useState<string | null>(null);
  // State to track if a response is loading
  const [isLoading, setIsLoading] = useState(false);
  // State to track any errors
  const [error, setError] = useState<string | null>(null);
  // State to track API health
  const [apiHealthy, setApiHealthy] = useState<boolean | null>(null);

  // This useEffect will only run on the client after hydration
  useEffect(() => {
    setIsMounted(true);
    
    // Check API health when the component mounts
    const checkApiHealth = async () => {
      try {
        const isHealthy = await AgentApi.checkHealth();
        setApiHealthy(isHealthy);
      } catch (error) {
        console.error('API health check failed:', error);
        setApiHealthy(false);
      }
    };
    
    checkApiHealth();
  }, []);

  // Handler for when a request is submitted
  const handleRequestSubmit = async (request: string) => {
    setUserRequest(request);
    
    // Create a new user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      content: request,
      sender: 'user',
      timestamp: Date.now()
    };
    
    // Add the user message to the messages array
    setMessages([...messages, userMessage]);
    
    setRequestSent(true);
    setIsLoading(true);
    setError(null);
    
    try {
      // Call the agent API
      const response = await AgentApi.sendMessage(request, sessionId);
      
      // Store the session ID for future requests
      setSessionId(response.session_id);
      
      // For demo purposes, generate mock tool call data
      // In a real implementation, this would come from the backend
      const mockToolCalls: ToolCallData[] = [
        {
          id: `tool-call-${Date.now()}`,
          toolName: 'SearchPatents',
          inputs: {
            query: 'autonomous navigation',
            center: 'JPL',
            max_results: 5
          },
          output: JSON.stringify({
            status: 'success',
            query: 'autonomous navigation',
            total_found: 42,
            returning: 5,
            results: [
              {
                id: 'PAT123456',
                case_number: 'NASA-PAT-001',
                title: 'Autonomous Navigation System for Space Exploration',
                description: 'A system for autonomous navigation of spacecraft in deep space exploration missions.',
                primary_contact: 'John Doe',
                category: 'Navigation',
                website: 'https://technology.nasa.gov/patent/PAT123456',
                status: 'Granted',
                date: '2023-05-15',
                center: 'JPL'
              },
              {
                id: 'PAT789012',
                case_number: 'NASA-PAT-002',
                title: 'Terrain-based Navigation for Planetary Rovers',
                description: 'A method for rover navigation using terrain feature recognition and mapping.',
                primary_contact: 'Jane Smith',
                category: 'Navigation',
                website: 'https://technology.nasa.gov/patent/PAT789012',
                status: 'Granted',
                date: '2022-11-30',
                center: 'JPL'
              }
            ]
          }),
          timestamp: Date.now()
        }
      ];
      
      // Create an agent message
      const agentMessage: Message = {
        id: `agent-${Date.now()}`,
        content: response.response,
        sender: 'agent',
        timestamp: Date.now(),
        toolCalls: mockToolCalls // Add the mock tool calls for demonstration
      };
      
      // Add the agent message to the messages array
      setMessages(prevMessages => [...prevMessages, agentMessage]);
      
    } catch (error: any) {
      console.error('Error calling agent API:', error);
      setError(`Error: ${error.message || 'Failed to get response from the agent'}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Handler for starting a new conversation
  const handleReset = async () => {
    // If we have a session ID, delete it from the server
    if (sessionId) {
      try {
        await AgentApi.deleteSession(sessionId);
      } catch (error) {
        console.error('Error deleting session:', error);
      }
    }
    
    // Reset all local state
    setRequestSent(false);
    setUserRequest('');
    setMessages([]);
    setDisplayItems([]);
    setSessionId(null);
    setError(null);
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
            
            {/* API Health Status */}
            {apiHealthy === false && (
              <div className="mb-4 p-3 bg-red-900/50 text-white rounded-md">
                Warning: Agent API is not available. Responses will not work.
              </div>
            )}
            
            <div className="w-full">
              <ChatInput 
                onSubmit={handleRequestSubmit} 
                placeholder=""
                autoFocus
                disabled={apiHealthy === false}
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
            messages={messages}
            onNewRequest={handleRequestSubmit} 
            onReset={handleReset} 
            isLoading={isLoading}
            error={error}
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
