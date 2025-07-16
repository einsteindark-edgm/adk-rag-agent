# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project exposes a Google ADK (Agent Development Kit) RAG agent through the A2A (Agent-to-Agent) protocol. The architecture uses:
- **ADK**: To create the agent with RAG tools for Vertex AI
- **A2A**: To expose the ADK agent to other agents via standardized protocol
- **Runner**: ADK's asynchronous execution engine with session management

## Architecture

### Project Structure
```
app/
├── domain/              # Business entities (Document, Corpus)
├── infrastructure/      # External services and implementations
│   ├── agent.py        # ADK agent definition
│   ├── tools/          # RAG tool implementations
│   ├── web/            # A2A executor
│   ├── a2a/            # Agent card definition
│   └── config/         # Configuration
└── main/               # Server entry point
```

### Architecture Flow
```
A2A Client
    ↓
A2A Protocol (DefaultRequestHandler)
    ↓
RAGAgentExecutor
    ↓
ADK Runner (manages sessions, memory, artifacts)
    ↓
ADK Agent (root_agent)
    ↓
RAG Tools (query, create, delete, etc.)
```

### Key Components

1. **ADK Agent** (`app/infrastructure/agent.py`)
   - Defines the agent with tools and instructions
   - Uses Gemini 2.5 Flash model
   - Contains all RAG tool references

2. **ADK Runner** (`app/main/a2a_main.py`)
   - Manages agent execution asynchronously
   - Handles sessions, memory, and artifacts
   - Created with: `Runner(app_name, agent, services...)`

3. **RAGAgentExecutor** (`app/infrastructure/web/rag_agent_executor.py`)
   - Implements A2A's AgentExecutor interface
   - Uses `runner.run_async()` to execute agent
   - Handles event streaming and task updates

4. **A2A Server** (`app/main/a2a_main.py`)
   - Creates Runner with ADK agent
   - Sets up A2A protocol handlers
   - Exposes agent at http://localhost:8080

## Development Commands

### Setup and Installation
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up Google Cloud authentication
gcloud auth application-default login
gcloud services enable aiplatform.googleapis.com
```

### Running the A2A Server
```bash
# Start A2A server (from project root)
python __main__.py

# Server runs at http://localhost:8080
# Agent card available at http://localhost:8080/.well-known/agent.json
```

### Testing with A2A Client
```bash
# Interactive mode
python a2a_client.py

# Automated tests
python a2a_client.py --test
```

### Testing ADK Agent Directly
```bash
# Test agent without A2A layer
adk run
```

### Environment Configuration
Create a `.env` file in the root directory:
```env
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
A2A_HOST=0.0.0.0
A2A_PORT=8080
AGENT_MODEL=gemini-2.0-flash-exp
```

## Available Tools
1. `rag_query` - Query documents with natural language
2. `list_corpora` - List all available corpora
3. `create_corpus` - Create new document corpus
4. `add_data` - Add documents from Google Drive or GCS
5. `get_corpus_info` - Get detailed corpus information
6. `delete_document` - Remove specific documents
7. `delete_corpus` - Delete entire corpus

## Common Development Tasks

### Adding a New Tool
1. Create new file in `app/infrastructure/tools/`
2. Implement tool function following ADK patterns (with ToolContext parameter)
3. Import and add to tools list in `app/infrastructure/agent.py`
4. Update agent instructions in `app/infrastructure/agent.py`

### Important Files
- `__main__.py` - Entry point for A2A server
- `app/main/a2a_main.py` - A2A server setup with Runner
- `app/infrastructure/web/rag_agent_executor.py` - A2A executor using Runner
- `app/infrastructure/agent.py` - ADK agent definition with tools
- `app/infrastructure/tools/` - RAG tool implementations
- `a2a_client.py` - Test client for A2A

## How Runner Works

The ADK Runner is the key component that executes the agent:

1. **Creation**: `Runner(app_name, agent, artifact_service, session_service, memory_service)`
2. **Execution**: `runner.run_async(session_id, user_id, new_message)`
3. **Events**: Returns AsyncGenerator of events
   - Intermediate updates
   - Function calls
   - Final response

## A2A Protocol Details

### Message Format
```json
{
  "message": {
    "parts": [{
      "root": {
        "text": "Your message here"
      }
    }]
  }
}
```

### Event Flow
1. A2A receives message
2. RAGAgentExecutor converts A2A parts to GenAI parts
3. Runner executes agent asynchronously
4. Events are streamed back:
   - Task state updates (working)
   - Intermediate responses
   - Final response (completed)

## Debugging
- Check A2A server logs for protocol issues
- Monitor Runner events in RAGAgentExecutor
- Check ADK agent logs for tool execution
- Test agent directly with `adk run` to isolate issues
- Verify agent card at `/.well-known/agent.json`
- Check Google Cloud logs for Vertex AI operations
- Verify authentication: `gcloud auth list`