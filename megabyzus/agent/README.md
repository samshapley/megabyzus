# Calculator Agent with Modular Tool-Calling Architecture

This implementation demonstrates a modular approach to building tool-calling agents with Anthropic's Claude API. It separates the generic tool-calling logic from the domain-specific calculator functionality.

## Features

- **Modular Architecture**:
  - `tool_calling_agent.py`: Generic base agent that handles conversation memory, API calls, and tool use
  - `calculator_agent.py`: Domain-specific agent focused on calculator operations
  - `calculator_tools.py`: Tool definitions and implementations for calculator operations

- **Calculator Tools**:
  - `add`: Add multiple numbers together
  - `subtract`: Subtract one number from another
  - `multiply`: Multiply multiple numbers together
  - `divide`: Divide one number by another

- **Benefits**:
  - Full conversation memory (messages list grows with each interaction)
  - Easy to extend with new tools
  - Reusable base agent for other domains
  - Clean separation of concerns

## Getting Started

### Prerequisites

- Python 3.6+
- Required packages: `anthropic`, `pydantic`

### Installation

1. Install required packages:

```bash
pip install anthropic pydantic 'pydantic[email]'
```

2. Set your Anthropic API key as an environment variable:

```bash
export ANTHROPIC_API_KEY='your_api_key_here'
```

## Usage

### Basic Usage of Calculator Agent

```python
from megabyzus.agent.calculator_agent import CalculatorAgent

# Initialize calculator agent
agent = CalculatorAgent()

# Process a user message
response = agent.process_message("What is 42 plus 18?")
print(f"Agent: {response}")

# Process another message that references the previous calculation
response = agent.process_message("Multiply that result by 2.5")
print(f"Agent: {response}")

# View conversation history
print(agent.get_conversation_history())
```

### Creating Your Own Tool-Calling Agent

You can use the base `ToolCallingAgent` class to create your own domain-specific agents:

```python
from megabyzus.agent.tool_calling_agent import ToolCallingAgent

# Define your tools and process_tool_call function
my_tools = [...]
def process_my_tool_call(tool_name, tool_input):
    # Process the tool call and return a result
    pass

# Create a custom agent
my_agent = ToolCallingAgent(
    tools=my_tools,
    process_tool_call_func=process_my_tool_call
)

# Use the agent
response = my_agent.process_message("Your message here")
print(f"Response: {response}")
```

### Running the Test Script

To run the included test script:

```bash
cd megabyzus/agent
python test_calculator_agent.py
```

The test script demonstrates the agent's capabilities with a series of calculations, showing how conversation memory allows the agent to reference previous results.

### Example Conversation

```
User: What is 42 plus 18?
Agent: Therefore, 42 plus 18 equals 60.

User: Multiply that result by 2.5
Agent: So, if we multiply the previous result of 60 by 2.5, we get 150.

User: If I divide the previous result by 15, what do I get?
Agent: Therefore, if you divide the previous result of 150 by 15, you get 10.
```

## How It Works

1. **ToolCallingAgent (Base Agent)**:
   - Handles initialization of the Anthropic client
   - Manages conversation memory
   - Processes user messages and sends them to Claude
   - Detects and processes tool calls
   - Formats and returns responses

2. **CalculatorAgent (Domain-Specific)**:
   - Extends the base agent functionality with calculator-specific tools
   - Delegates the core logic to the base agent
   - Provides a simple interface focused on calculator operations

3. **calculator_tools.py**:
   - Defines Pydantic models for tool input validation
   - Implements the calculator functions
   - Processes tool calls and returns results

## Architecture Benefits

This modular architecture allows for:

1. **Code Reuse**: The base agent handles all the common logic for any tool-calling agent
2. **Maintainability**: Domain-specific code is separate from the generic code
3. **Extensibility**: Easy to add new tools or create new types of agents
4. **Testing**: Each component can be tested independently