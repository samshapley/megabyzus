/**
 * Type definitions for the Megabyzus UI components
 */

// Tool Call Stages
export type ToolCallStage = 'pending' | 'completed';

// Tool Call Data
export interface ToolCallData {
  id: string;
  toolName: string;
  inputs: Record<string, any>;
  output: any;
  timestamp: number;
  stage?: ToolCallStage; // Add stage to track tool call status
  isExpanded?: boolean; // Track expansion state of the tool call panel
}

// Base Message type (used in existing components)
export type Message = {
  id: string;
  content: string;
  sender: 'user' | 'agent';
  timestamp: number;
  toolCalls?: ToolCallData[]; // Tool calls associated with this message
  toolCallsPending?: boolean; // Flag to indicate if this message has pending tool calls
};

// Tab selection for tool call display
export type ToolCallTab = 'input' | 'output';