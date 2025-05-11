'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import ChatInput from '@/components/chat/ChatInput';
import ResponsePanel from '@/components/chat/ResponsePanel';
import DisplayPanel from '@/components/display/DisplayPanel';
import RootLayout from '@/components/layout/RootLayout';
import AgentApi from '@/services/api';
import { Message, ToolCallData, ToolCallStage } from '@/types';

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
  // State to track if we're processing tool calls
  const [processingTools, setProcessingTools] = useState(false);

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

  // Update tool call statuses in a message
  const updateToolCallsInMessage = (messageId: string, updatedToolCalls: ToolCallData[]) => {
    setMessages(prevMessages => 
      prevMessages.map(message => {
        if (message.id === messageId && message.toolCalls) {
          // Update the tool calls in this message
          return {
            ...message,
            toolCalls: message.toolCalls.map(existingToolCall => {
              // Find the updated tool call with the same ID
              const updatedToolCall = updatedToolCalls.find(tc => tc.id === existingToolCall.id);
              if (updatedToolCall) {
                // If found, return the updated version
                return {
                  ...existingToolCall,
                  ...updatedToolCall,
                  stage: 'completed' as ToolCallStage,
                  output: updatedToolCall.output
                };
              }
              return existingToolCall;
            }),
            // All tool calls are no longer pending
            toolCallsPending: updatedToolCalls.some(tc => tc.status === 'pending')
          };
        }
        return message;
      })
    );
  };

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
      
      // Get the tool calls from the response (initially in pending state)
      const toolCalls = response.toolCalls || [];
      
      // Create a timestamp for the agent message ID to ensure consistency
      const agentMessageId = `agent-${Date.now()}`;
      
      // Determine if there are any pending tool calls
      const hasPendingToolCalls = toolCalls.length > 0;
      
      // If there are tool calls, set the processing state to true
      if (hasPendingToolCalls) {
        setProcessingTools(true);
      }
      
      // Add stage information to tool calls
      const enhancedToolCalls = toolCalls.map(toolCall => ({
        ...toolCall,
        stage: hasPendingToolCalls ? 'pending' as ToolCallStage : 'completed' as ToolCallStage,
        isExpanded: false // Default to collapsed
      }));

      // Create the agent message with the response text and tool calls
      const agentMessage: Message = {
        id: agentMessageId,
        content: response.response,
        sender: 'agent',
        timestamp: Date.now(),
        toolCalls: enhancedToolCalls.length > 0 ? enhancedToolCalls : undefined,
        toolCallsPending: hasPendingToolCalls
      };
      
      // Add the agent message to the messages array
      setMessages(prevMessages => [...prevMessages, agentMessage]);
      
      // Start polling for tool call results if there are pending tool calls
      if (hasPendingToolCalls && sessionId) {
        const toolCallIds = toolCalls.map(tc => tc.id);
        
        // Poll for results and update the UI
        AgentApi.pollToolCallResults(
          response.session_id,
          toolCallIds,
          (updatedToolCalls) => {
            // Update the tool calls in the message with the latest results
            updateToolCallsInMessage(agentMessageId, updatedToolCalls);
            
            // Check if all tool calls are completed
            const allCompleted = updatedToolCalls.every(
              tc => tc.status === 'completed' || tc.status === 'error' || tc.status === 'not_found'
            );
            
            // If all tool calls are completed, set the processing state to false
            if (allCompleted) {
              setProcessingTools(false);
            }
          }
        ).then(() => {
          // All tool calls are completed or timeout reached
          setProcessingTools(false);
        }).catch(error => {
          console.error('Error polling for tool call results:', error);
          setProcessingTools(false);
        });
      }
    } catch (error: any) {
      console.error('Error calling agent API:', error);
      setError(`Error: ${error.message || 'Failed to get response from the agent'}`);
      setProcessingTools(false);
    } finally {
      setIsLoading(false);
      
      // Note: We don't set processingTools to false here because it might still be processing
      // The polling function will set it to false when all tools are completed
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
    setProcessingTools(false);
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
            processingTools={processingTools}
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