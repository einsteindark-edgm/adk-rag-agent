# ADK Agent with A2A Protocol and Clean Architecture Integration Guide

This guide documents how to integrate a Google ADK (Agent Development Kit) agent with Clean Architecture using the A2A (Agent-to-Agent) protocol, based on real implementation experience.

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Implementation Steps](#implementation-steps)
5. [Common Errors and Solutions](#common-errors-and-solutions)
6. [Testing](#testing)

## Architecture Overview

The integration consists of:
- **ADK Agent**: Core agent logic using Google's Agent Development Kit
- **Clean Architecture**: Domain, Use Cases, Infrastructure layers
- **A2A Protocol**: JSON-RPC based communication protocol
- **A2A Server**: Exposes the ADK agent via HTTP using A2A protocol
- **A2A Client**: Communicates with the agent using JSON-RPC

```
┌─────────────────┐     JSON-RPC      ┌──────────────────┐
│   A2A Client    │ ←---------------→ │   A2A Server     │
└─────────────────┘                   └──────────────────┘
                                               │
                                               ▼
                                      ┌──────────────────┐
                                      │  Clean Arch      │
                                      │  ┌────────────┐  │
                                      │  │   Domain   │  │
                                      │  └────────────┘  │
                                      │  ┌────────────┐  │
                                      │  │ Use Cases  │  │
                                      │  └────────────┘  │
                                      │  ┌────────────┐  │
                                      │  │Infrastructure│ │
                                      │  └────────────┘  │
                                      └──────────────────┘
                                               │
                                               ▼
                                      ┌──────────────────┐
                                      │   ADK Agent      │
                                      │  - Tools         │
                                      │  - Runner         │
                                      │  - Session Mgmt  │
                                      └──────────────────┘
```

## Project Structure

```
project-root/
├── app/
│   ├── domain/
│   │   ├── entities/
│   │   │   └── agent.py
│   │   └── repositories/
│   │       └── agent_repository.py
│   ├── use_cases/
│   │   └── agent_use_cases.py
│   ├── infrastructure/
│   │   ├── tools/           # ADK tools
│   │   │   ├── __init__.py
│   │   │   └── your_tool.py
│   │   ├── web/
│   │   │   ├── __init__.py
│   │   │   └── rag_agent_executor.py  # A2A integration
│   │   └── config/
│   │       └── agent_config.py
│   └── main/
│       └── a2a_main.py     # A2A server entry point
├── requirements.txt
└── a2a_client.py          # Example client
```

## Core Components

### 1. Requirements (requirements.txt)

```txt
google-adk==0.5.0
a2a-sdk>=0.2.11
uvicorn>=0.34.0
httpx>=0.27.0
python-dotenv==1.0.1
pydantic>=2.10.4
```

### 2. A2A Server Main Entry Point (app/main/a2a_main.py)

```python
"""A2A server entry point for the ADK agent."""

import uvicorn
from a2a import A2A
from app.infrastructure.web import agent

def main():
    """Run the A2A server."""
    # Configure A2A with your agent
    a2a = A2A(agent)
    
    # Run with uvicorn
    uvicorn.run(
        a2a,
        host="0.0.0.0",
        port=8006,
        log_level="info"
    )

if __name__ == "__main__":
    main()
```

### 3. Agent Infrastructure Module (app/infrastructure/web/__init__.py)

```python
"""Web infrastructure for the agent."""

from a2a import Agent as A2AAgent
from .rag_agent_executor import RagAgentExecutor

# Create executor instance
executor = RagAgentExecutor()

# Create A2A agent
agent = A2AAgent(
    name="Your Agent Name",
    version="1.0.0",
    description="Your agent description",
    executor=executor
)

__all__ = ["agent", "executor"]
```

### 4. Agent Executor Implementation (app/infrastructure/web/rag_agent_executor.py)

```python
"""Agent executor that integrates ADK with A2A protocol."""

import logging
from typing import AsyncIterator
from google.adk import llm
from google.adk.common import event
from google.adk.runner import Runner
from a2a import Executor, AgentMessage, ToolCallSpec, TaskContext, TaskUpdater, Part, TextPart

logger = logging.getLogger(__name__)

class RagAgentExecutor(Executor):
    """Executor that bridges ADK agent with A2A protocol."""

    def __init__(self):
        """Initialize the executor."""
        # Create ADK runner
        self.runner = Runner(
            tools=self._get_tools(),
            system_instruction=self._get_system_instruction(),
        )
        logger.info("RagAgentExecutor initialized")

    def _get_tools(self):
        """Get ADK tools for the agent."""
        from ..tools import tool1, tool2  # Import your tools
        return [tool1, tool2]

    def _get_system_instruction(self) -> str:
        """Get system instruction for the agent."""
        return """You are a helpful assistant. Use the available tools to help users."""

    async def execute(
        self,
        *,
        session_id: str,
        messages: list[AgentMessage],
        context: TaskContext,
        tool_specs: list[ToolCallSpec],
        updater: TaskUpdater | None = None,
    ) -> None:
        """Execute agent request using A2A protocol.
        
        CRITICAL: This method is called by A2A server for each request.
        """
        if not messages:
            return

        # Get the latest user message
        latest_message = messages[-1]
        new_message = self._convert_a2a_message_to_adk(latest_message)
        
        # Create task updater if provided
        task_updater = updater

        # Submit new task if needed
        if not context.current_task:
            await updater.submit()
            
        # Start work
        await updater.start_work()

        # Run ADK agent
        async for event in self._run_agent(session_id, new_message):
            if event.is_final_response():
                # Final response from agent
                parts = self._convert_genai_parts_to_a2a(
                    event.content.parts if event.content and event.content.parts else []
                )
                logger.debug("Yielding final response: %s", parts)
                
                # Add response as artifact and complete
                await task_updater.add_artifact(parts)
                await task_updater.complete()
                break
                
            elif not event.get_function_calls():
                # Intermediate update (not a function call)
                logger.debug("Yielding update response")
                await task_updater.update_status(
                    TaskState.working,
                    message=task_updater.new_agent_message(
                        self._convert_genai_parts_to_a2a(
                            event.content.parts if event.content and event.content.parts else []
                        )
                    ),
                )

    async def _run_agent(
        self, session_id: str, message: llm.Message
    ) -> AsyncIterator[event.Event]:
        """Run the ADK agent with a message."""
        # Get or create session
        session = self.runner.get_session(session_id)
        if not session:
            session = self.runner.create_session(session_id=session_id)
            
        # Execute the agent
        async for event in session.run_async(message):
            yield event

    def _convert_a2a_message_to_adk(self, message: AgentMessage) -> llm.Message:
        """Convert A2A message to ADK message format."""
        parts = []
        for part in message.parts:
            if hasattr(part.root, 'text'):
                parts.append(llm.TextPart(text=part.root.text))
        
        return llm.Message(
            role=message.role,
            parts=parts
        )

    def _convert_genai_parts_to_a2a(self, parts: list) -> list[Part]:
        """Convert GenAI parts to A2A parts."""
        return [
            Part(root=TextPart(text=part.text))
            for part in parts
            if hasattr(part, 'text')
        ]
```

### 5. ADK Tools (app/infrastructure/tools/your_tool.py)

```python
"""Example ADK tool implementation."""

def your_tool(param1: str, param2: int) -> dict:
    """Your tool description.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        dict: Tool result
    """
    # Tool implementation
    return {
        "status": "success",
        "result": f"Processed {param1} with {param2}"
    }
```

### 6. A2A Client Implementation (a2a_client.py)

```python
"""A2A client for interacting with the agent."""
import asyncio
import uuid
import httpx

class A2AClient:
    """Client for A2A protocol communication."""
    
    def __init__(self, agent_url: str = "http://localhost:8006"):
        """Initialize with agent URL."""
        self.agent_url = agent_url
        self.httpx_client = httpx.AsyncClient(timeout=30.0)
        self.session_id = f"session-{uuid.uuid4().hex[:8]}"
    
    async def connect(self):
        """Connect to the agent."""
        response = await self.httpx_client.get(f"{self.agent_url}/.well-known/agent.json")
        if response.status_code == 200:
            agent_info = response.json()
            print(f"✅ Connected to {agent_info['name']} v{agent_info['version']}")
        else:
            raise Exception(f"Failed to connect: {response.status_code}")
    
    async def send_message(self, message: str) -> str:
        """Send a message using JSON-RPC protocol."""
        # Create JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "message/send",
            "params": {
                "message": {
                    "messageId": str(uuid.uuid4()),
                    "role": "user",
                    "parts": [
                        {
                            "text": message
                        }
                    ]
                },
                "sessionId": self.session_id
            }
        }
        
        response = await self.httpx_client.post(
            self.agent_url,
            json=request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                return self._extract_text_from_result(result["result"])
            elif "error" in result:
                return f"Error: {result['error'].get('message', 'Unknown error')}"
        
        return f"HTTP Error {response.status_code}"
    
    def _extract_text_from_result(self, result):
        """Extract text from JSON-RPC result."""
        if isinstance(result, dict):
            # Look for artifacts (the actual response format)
            if "artifacts" in result and result["artifacts"]:
                texts = []
                for artifact in result["artifacts"]:
                    if "parts" in artifact:
                        for part in artifact["parts"]:
                            if "text" in part:
                                texts.append(part["text"])
                if texts:
                    return "\n".join(texts)
        return "No response text found"
    
    async def close(self):
        """Close the client connection."""
        await self.httpx_client.aclose()
```

## Implementation Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create ADK Tools
Place your ADK tools in `app/infrastructure/tools/`. Each tool should follow ADK conventions:
```python
def tool_name(param: type) -> return_type:
    """Tool description."""
    # Implementation
```

### 3. Configure the Agent
Update `app/infrastructure/web/rag_agent_executor.py`:
- Add your tools in `_get_tools()`
- Set your system instruction in `_get_system_instruction()`

### 4. Run the A2A Server
```bash
python -m app.main.a2a_main
```

### 5. Test with Client
```python
async def test():
    client = A2AClient()
    await client.connect()
    response = await client.send_message("Your message here")
    print(response)
    await client.close()

asyncio.run(test())
```

## Common Errors and Solutions

### Error 1: "TypeError: A2AClient.__init__() missing 1 required positional argument: 'httpx_client'"

**Cause**: The A2A SDK API changed between versions.

**Solution**: Don't pass httpx_client to A2AClient. Create it internally:
```python
# Wrong (old API)
httpx_client = httpx.AsyncClient()
client = A2AClient(agent_url, httpx_client)

# Correct (new API)
client = A2AClient(agent_url)  # httpx_client created internally
```

### Error 2: "ERROR: Could not find a version that satisfies the requirement a2a==0.1.0"

**Cause**: Wrong package name or version.

**Solution**: Use the correct package name and version:
```txt
# Wrong
a2a==0.1.0

# Correct
a2a-sdk>=0.2.11
```

### Error 3: "object NoneType can't be used in 'await' expression"

**Cause**: Confusion about which ADK methods are sync vs async.

**Solution**: 
- `runner.get_session()` and `runner.create_session()` are **synchronous**
- `TaskUpdater` methods (`submit()`, `start_work()`, `add_artifact()`, `complete()`) are **asynchronous**

```python
# Correct usage
session = self.runner.get_session(session_id)  # No await
await updater.submit()  # With await
```

### Error 4: Response showing full JSON instead of extracted text

**Cause**: Client not properly extracting text from the A2A response structure.

**Solution**: The response structure is:
```json
{
  "result": {
    "artifacts": [
      {
        "parts": [
          {
            "text": "The actual response text"
          }
        ]
      }
    ]
  }
}
```

Extract with: `result['artifacts'][0]['parts'][0]['text']`

### Error 5: Import errors with ADK tools

**Cause**: Incorrect import paths or missing __init__.py files.

**Solution**: Ensure proper package structure:
```
app/
  infrastructure/
    tools/
      __init__.py  # Must exist
      your_tool.py
```

Import as:
```python
from app.infrastructure.tools import your_tool
```

## Testing

### 1. Test Server Health
```bash
curl http://localhost:8006/.well-known/agent.json
```

### 2. Test with Simple Client
```python
#!/usr/bin/env python
import asyncio
from a2a_client import A2AClient

async def main():
    client = A2AClient()
    await client.connect()
    
    # Test your agent
    response = await client.send_message("Hello")
    print(f"Response: {response}")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Best Practices

1. **Always check ADK method signatures** - Some are sync, some are async
2. **Use proper A2A response format** - Responses must be in artifacts
3. **Handle sessions properly** - Create if doesn't exist
4. **Add comprehensive logging** - Helps debug A2A/ADK integration issues
5. **Test incrementally** - Start with simple tools, add complexity gradually
6. **Follow Clean Architecture** - Keep ADK tools in infrastructure layer

## Debugging Tips

1. **Enable all logging**:
```python
logging.getLogger('app').setLevel(logging.DEBUG)
logging.getLogger('google.adk').setLevel(logging.DEBUG)
logging.getLogger('a2a').setLevel(logging.DEBUG)
```

2. **Check raw responses**:
```python
print(f"Raw response: {response.json()}")
```

3. **Verify tool registration**:
```python
print(f"Registered tools: {self.runner.tools}")
```

4. **Monitor session state**:
```python
print(f"Session exists: {self.runner.get_session(session_id) is not None}")
```