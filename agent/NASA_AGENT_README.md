# NASA Technology Transfer Tool-Calling Agent

This implementation demonstrates a modular approach to building a tool-calling agent for NASA's Technology Transfer API using Anthropic's Claude API. The agent allows users to search and explore NASA's technology portfolio including patents, software, and commercial spinoffs.

## Features

- **Modular Architecture**:
  - `tool_calling_agent.py`: Generic base agent that handles conversation memory, API calls, and tool use
  - `nasa_agent.py`: Domain-specific agent focused on NASA Technology Transfer API operations
  - `nasa_tools.py`: Tool definitions and implementations for NASA API operations

- **NASA Technology Tools**:
  - `SearchPatents`: Search for NASA patents matching specific criteria
  - `SearchSoftware`: Search for NASA software matching specific criteria  
  - `SearchSpinoffs`: Search for NASA spinoff technologies matching specific criteria

- **Benefits**:
  - Full conversation memory (messages list grows with each interaction)
  - Easy to extend with new tools
  - Reusable base agent for other domains
  - Clean separation of concerns

## Getting Started

### Prerequisites

- Python 3.6+
- Required packages: `anthropic`, `pydantic`, `requests`

### Installation

1. Install required packages:

```bash
pip install anthropic pydantic 'pydantic[email]'
```

2. Install the megabyzus package in development mode:

```bash
pip install -e /path/to/megabyzus
```

3. Set your Anthropic API key as an environment variable:

```bash
export ANTHROPIC_API_KEY='your_api_key_here'
```

## Usage

### Basic Usage of NASA Agent

```python
from megabyzus.agent.nasa_agent import NASAAgent

# Initialize NASA agent
agent = NASAAgent()

# Process a user message
response = agent.process_message("I'm looking for NASA patents related to propulsion systems. Can you find some for me?")
print(f"Agent: {response}")

# Process another message that references the previous search
response = agent.process_message("Are there any similar technologies from JPL?")
print(f"Agent: {response}")

# View conversation history
print(agent.get_conversation_history())
```

### Testing the NASA Agent

You can use the included test scripts:

1. To test with mock API responses (no API key required):
```bash
python -m megabyzus.agent.nasa_agent_mock_test
```

2. To test with real API calls (requires API key):
```bash
python -m megabyzus.agent.test_nasa_agent
```

## How It Works

1. **ToolCallingAgent (Base Agent)**:
   - Handles initialization of the Anthropic client
   - Manages conversation memory
   - Processes user messages and sends them to Claude
   - Detects and processes tool calls
   - Formats and returns responses

2. **NASAAgent (Domain-Specific)**:
   - Extends the base agent functionality with NASA-specific tools
   - Delegates the core logic to the base agent
   - Provides a simple interface focused on NASA technology operations

3. **nasa_tools.py**:
   - Defines Pydantic models for tool input validation
   - Implements the NASA API interaction functions
   - Processes tool calls and returns results

## Architecture Benefits

This modular architecture allows for:

1. **Code Reuse**: The base agent handles all the common logic for any tool-calling agent
2. **Maintainability**: Domain-specific code is separate from the generic code
3. **Extensibility**: Easy to add new tools or create new types of agents
4. **Testing**: Each component can be tested independently

## Tools Functionality

### Search Patents

Searches for NASA patents matching specific criteria:

- `query`: Search term or keywords (required)
- `center`: Filter by NASA center (optional)
- `max_results`: Maximum number of results to return (optional)

### Search Software

Searches for NASA software matching specific criteria:

- `query`: Search term or keywords (required)
- `center`: Filter by NASA center (optional)
- `max_results`: Maximum number of results to return (optional)

### Search Spinoffs

Searches for NASA spinoff technologies matching specific criteria:

- `query`: Search term or keywords (required)
- `center`: Filter by NASA center (optional)
- `max_results`: Maximum number of results to return (optional)

## Example Conversation

```
User: I'm looking for NASA patents related to propulsion systems. Can you find some for me?

Agent: I found 2 NASA patents related to propulsion systems. The first is an 'Advanced Propulsion System' from Glenn Research Center, which uses quantum mechanics. The second is an 'Improved Rocket Engine' from Johnson Space Center, which increases efficiency and reduces fuel consumption. Both patents are available for licensing.

User: What software has NASA developed for image processing?

Agent: NASA has developed several software packages for image processing. The NASA Image Processing Toolkit from Goddard Space Flight Center provides comprehensive tools for processing and analyzing scientific imagery. There's also an Advanced Visualization Suite from Ames Research Center for 3D visualization of complex data sets. The Image Processing Toolkit is available as open source while the Visualization Suite is available for government purposes.
```

## Further Development

This implementation can be extended with additional tools:

1. Add technology details and analysis tools
2. Implement visualization and reporting tools
3. Add recommendation and filtering capabilities

The modular design makes it easy to add new tools or enhance existing ones.