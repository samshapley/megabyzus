/**
 * Agent API Service
 * 
 * This service handles all communication with the agent API.
 */

import { ToolCallData } from '@/types';

// Types for API requests and responses
export interface MessageRequest {
  message: string;
  session_id?: string;
}

export interface MessageResponse {
  response: string;
  session_id: string;
  toolCalls?: ToolCallData[]; // Add tool calls to response
}

export interface ToolCallStatusRequest {
  session_id: string;
  tool_call_ids: string[];
}

export interface ToolCallStatusResponse {
  tool_calls: ToolCallStatus[];
}

export interface ToolCallStatus {
  tool_call_id: string;
  status: 'pending' | 'completed' | 'error' | 'not_found';
  result?: any;
  toolName?: string;
  inputs?: Record<string, any>;
  timestamp?: number;
}

export interface ConversationHistory {
  session_id: string;
  history: any[];
}

// API base URL - Use relative URL to work with Next.js rewrites
// This will be rewritten to the actual API URL by Next.js
const API_BASE_URL = '';

/**
 * Agent API client
 */
export const AgentApi = {
  /**
   * Send a message to the agent API 
   * 
   * @param message The user's message
   * @param sessionId Optional session ID for conversation continuity
   * @returns The agent's response with session information
   */
  async sendMessage(message: string, sessionId?: string): Promise<MessageResponse> {
    try {
      console.log(`Sending message to agent API: ${message}`);
      
      const response = await fetch(`${API_BASE_URL}/api/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          session_id: sessionId
        } as MessageRequest),
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Response received:', data);
      
      return data as MessageResponse;
    } catch (error) {
      console.error('Error sending message to agent:', error);
      throw error;
    }
  },

  /**
   * Check the status of pending tool calls
   * 
   * @param sessionId The session ID
   * @param toolCallIds Array of tool call IDs to check
   * @returns The status of each tool call
   */
  async checkToolCallStatus(sessionId: string, toolCallIds: string[]): Promise<ToolCallStatusResponse> {
    try {
      console.log(`Checking status of tool calls: ${toolCallIds.join(', ')}`);
      
      const response = await fetch(`${API_BASE_URL}/api/tool-call-status`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          tool_call_ids: toolCallIds
        } as ToolCallStatusRequest),
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Tool call status received:', data);
      
      return data as ToolCallStatusResponse;
    } catch (error) {
      console.error('Error checking tool call status:', error);
      throw error;
    }
  },

  /**
   * Poll for tool call results until all are completed
   * 
   * @param sessionId The session ID
   * @param toolCallIds Array of tool call IDs to poll
   * @param callback Function to call when tool call status changes
   * @param interval Polling interval in milliseconds
   * @param timeout Maximum time to poll in milliseconds
   * @returns Promise that resolves when all tool calls are completed or timeout is reached
   */
  async pollToolCallResults(
    sessionId: string, 
    toolCallIds: string[], 
    callback: (toolCalls: ToolCallStatus[]) => void,
    interval: number = 1000,
    timeout: number = 60000
  ): Promise<ToolCallStatus[]> {
    const startTime = Date.now();
    let allCompleted = false;
    let latestResults: ToolCallStatus[] = [];
    
    // Initialize with pending status
    for (const id of toolCallIds) {
      latestResults.push({
        tool_call_id: id,
        status: 'pending'
      });
    }
    
    // Initial callback with pending status
    callback(latestResults);
    
    while (!allCompleted && (Date.now() - startTime < timeout)) {
      try {
        const response = await this.checkToolCallStatus(sessionId, toolCallIds);
        
        // Check if we have new information
        let statusChanged = false;
        
        for (const toolCall of response.tool_calls) {
          // Find corresponding result in our latest results
          const existingResult = latestResults.find(r => r.tool_call_id === toolCall.tool_call_id);
          
          if (existingResult) {
            // Check if status changed
            if (existingResult.status !== toolCall.status) {
              statusChanged = true;
              // Update the existing result
              existingResult.status = toolCall.status;
              existingResult.result = toolCall.result;
              existingResult.toolName = toolCall.toolName;
              existingResult.inputs = toolCall.inputs;
              existingResult.timestamp = toolCall.timestamp;
            }
          } else {
            // Add new result
            latestResults.push(toolCall);
            statusChanged = true;
          }
        }
        
        // If status changed, call the callback
        if (statusChanged) {
          callback(latestResults);
        }
        
        // Check if all are completed
        allCompleted = latestResults.every(r => r.status === 'completed' || r.status === 'error' || r.status === 'not_found');
        
        if (!allCompleted) {
          // Wait before polling again
          await new Promise(resolve => setTimeout(resolve, interval));
        }
      } catch (error) {
        console.error('Error polling for tool call results:', error);
        // Still wait before trying again
        await new Promise(resolve => setTimeout(resolve, interval));
      }
    }
    
    return latestResults;
  },
  
  /**
   * Get the conversation history for a session
   * 
   * @param sessionId The session ID
   * @returns The conversation history
   */
  async getConversationHistory(sessionId: string): Promise<ConversationHistory> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/history`);
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }
      
      return await response.json() as ConversationHistory;
    } catch (error) {
      console.error('Error fetching conversation history:', error);
      throw error;
    }
  },
  
  /**
   * Delete a session
   * 
   * @param sessionId The session ID to delete
   */
  async deleteSession(sessionId: string): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error deleting session:', error);
      throw error;
    }
  },
  
  /**
   * Check if the API is healthy
   * 
   * @returns True if the API is healthy, false otherwise
   */
  async checkHealth(): Promise<boolean> {
    try {
      console.log('Checking API health...');
      const response = await fetch(`${API_BASE_URL}/api/health`);
      const isHealthy = response.ok;
      console.log(`API health check result: ${isHealthy}`);
      return isHealthy;
    } catch (error) {
      console.error('API health check failed:', error);
      return false;
    }
  }
};

export default AgentApi;