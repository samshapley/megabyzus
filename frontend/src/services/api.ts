/**
 * NASA Agent API Service
 * 
 * This service handles all communication with the NASA agent API.
 */

// Types for API requests and responses
export interface MessageRequest {
  message: string;
  session_id?: string;
}

export interface MessageResponse {
  response: string;
  session_id: string;
}

export interface ConversationHistory {
  session_id: string;
  history: any[];
}

// API base URL - Use relative URL to work with Next.js rewrites
// This will be rewritten to the actual API URL by Next.js
const API_BASE_URL = '';

/**
 * NASA Agent API client
 */
export const nasaAgentApi = {
  /**
   * Send a message to the NASA agent
   * 
   * @param message The user's message
   * @param sessionId Optional session ID for conversation continuity
   * @returns The agent's response with session information
   */
  async sendMessage(message: string, sessionId?: string): Promise<MessageResponse> {
    try {
      console.log(`Sending message to NASA agent API: ${message}`);
      
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
      console.error('Error sending message to NASA agent:', error);
      throw error;
    }
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

export default nasaAgentApi;
