# Google ADK Samples - Vertex Search Grounding Agent

This repository contains a Google Agent Development Kit (ADK) sample that demonstrates how to create an agent with Vertex Search grounding capabilities.

## Overview

The Vertex Search Grounding Agent is designed to:
- Connect to Google's Vertex AI Search REST API for real-time information retrieval
- Ground agent responses with up-to-date, authoritative information
- Provide context-aware responses based on search results
- Handle multiple search queries and synthesize information

## Features

- **Vertex Search Integration**: Uses Google's Vertex AI Search REST API (not the Python client)
- **Response Grounding**: All agent responses are grounded with search results
- **Multi-Query Support**: Handle complex queries requiring multiple searches
- **Context Management**: Maintain conversation context across interactions
- **Error Handling**: Robust error handling for API failures and edge cases

## Prerequisites

- Google Cloud Project with Vertex AI API enabled
- Vertex Search Engine created in Vertex AI
- Python 3.8+
- Google Cloud credentials configured

## Installation

1. Clone this repository:
```bash
git clone https://github.com/your-org/google-adk-samples.git
cd google-adk-samples
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Google Cloud credentials:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your project settings
```

## Usage

### Basic Usage

```python
from agent import VertexSearchAgent

# Initialize the agent
agent = VertexSearchAgent()

# Ask a question
response = agent.ask("What are the latest developments in AI?")
print(response)
```

### Advanced Usage

```python
from agent import VertexSearchAgent

# Initialize with custom configuration
agent = VertexSearchAgent(
    project_id="your-project-id",
    search_engine_id="your-search-engine-id",
    max_results=10
)

# Start a conversation
conversation = agent.start_conversation()

# Add context
conversation.add_context("Focus on recent developments from 2024")

# Ask questions
response1 = conversation.ask("What are the latest AI breakthroughs?")
response2 = conversation.ask("How do these compare to previous years?")
```

## Configuration

### Environment Variables

- `GOOGLE_CLOUD_PROJECT`: Your Google Cloud Project ID
- `VERTEX_SEARCH_ENGINE_ID`: Your Vertex Search Engine ID
- `VERTEX_LOCATION`: Google Cloud region (default: us-central1)

### Agent Configuration

- `max_results`: Maximum number of search results to retrieve (default: 5)
- `search_type`: Type of search (web, news, etc.)
- `grounding_threshold`: Minimum confidence for grounding (default: 0.7)

## API Reference

### VertexSearchAgent

Main agent class for Vertex Search grounding.

#### Methods

- `ask(query: str) -> str`: Ask a single question
- `start_conversation() -> Conversation`: Start a multi-turn conversation
- `search(query: str) -> List[SearchResult]`: Perform a search query

### Conversation

Manages multi-turn conversations with context.

#### Methods

- `ask(query: str) -> str`: Ask a question in the conversation
- `add_context(context: str)`: Add context for future responses
- `get_history() -> List[Message]`: Get conversation history

## Examples

See the `examples/` directory for complete working examples:

- `basic_usage.py`: Simple question-answer example
- `conversation_example.py`: Multi-turn conversation example
- `custom_search.py`: Custom search configuration example

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.

## Notes

- This agent uses the Vertex AI Search REST API directly, as there is currently no public Python client for Vertex Search.
- Authentication is handled using Google Application Default Credentials (ADC). Ensure your environment is authenticated with Google Cloud (see [Authentication Guide](https://cloud.google.com/docs/authentication/getting-started)).