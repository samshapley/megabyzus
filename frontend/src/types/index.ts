/**
 * Type definitions for the Megabyzus UI components
 */

// Base Message type (used in existing components)
export type Message = {
    id: string;
    content: string;
    sender: 'user' | 'agent';
    timestamp: number;
    toolCalls?: ToolCallData[]; // New property
  };
  
  // Tool Call Data
  export interface ToolCallData {
    id: string;
    toolName: string;
    inputs: Record<string, any>;
    output: any;
    timestamp: number;
  }
  
  // Tab selection for tool call display
  export type ToolCallTab = 'input' | 'output';
  