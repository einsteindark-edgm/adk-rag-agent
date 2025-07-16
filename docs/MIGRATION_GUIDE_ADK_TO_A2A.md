# Migration Guide: ADK Agent to A2A + Clean Architecture

## Before Migration (Pure ADK)

```python
# Old: Direct ADK usage
from google.adk.runner import Runner
from google.adk import llm

# Create runner with tools
runner = Runner(
    tools=[tool1, tool2],
    system_instruction="You are a helpful assistant"
)

# Create session and run
session = runner.create_session()
response = session.run(llm.Message(role="user", parts=[llm.TextPart(text="Hello")]))
```

## After Migration (ADK + A2A + Clean Architecture)

### Step 1: Add Dependencies

```txt
# requirements.txt
google-adk==0.5.0
a2a-sdk>=0.2.11
uvicorn>=0.34.0
httpx>=0.27.0
```

### Step 2: Create Clean Architecture Structure

```bash
mkdir -p app/{domain,use_cases,infrastructure/{tools,web,config},main}
touch app/__init__.py
touch app/infrastructure/__init__.py
touch app/infrastructure/tools/__init__.py
touch app/infrastructure/web/__init__.py
```

### Step 3: Move Tools to Infrastructure Layer

```python
# app/infrastructure/tools/__init__.py
from .tool1 import tool1
from .tool2 import tool2

__all__ = ["tool1", "tool2"]
```

### Step 4: Create the Executor

```python
# app/infrastructure/web/rag_agent_executor.py
import logging
from typing import AsyncIterator
from google.adk import llm
from google.adk.runner import Runner
from a2a import Executor, AgentMessage, TaskContext, TaskUpdater, Part, TextPart, TaskState

logger = logging.getLogger(__name__)

class RagAgentExecutor(Executor):
    """Bridges ADK agent with A2A protocol."""

    def __init__(self):
        # Import tools from infrastructure
        from ..tools import tool1, tool2
        
        # Create ADK runner (same as before)
        self.runner = Runner(
            tools=[tool1, tool2],
            system_instruction="You are a helpful assistant"
        )

    async def execute(
        self,
        *,
        session_id: str,
        messages: list[AgentMessage],
        context: TaskContext,
        tool_specs: list,
        updater: TaskUpdater | None = None,
    ) -> None:
        """Execute request via A2A protocol."""
        if not messages:
            return

        # Convert A2A message to ADK format
        latest_message = messages[-1]
        adk_message = self._convert_to_adk_message(latest_message)
        
        # IMPORTANT: These are SYNC - no await!
        session = self.runner.get_session(session_id)
        if not session:
            session = self.runner.create_session(session_id=session_id)
        
        # IMPORTANT: These are ASYNC - use await!
        if not context.current_task:
            await updater.submit()
        await updater.start_work()

        # Run ADK agent
        async for event in session.run_async(adk_message):
            if event.is_final_response():
                # Convert response and complete task
                parts = self._convert_to_a2a_parts(event.content.parts)
                await updater.add_artifact(parts)
                await updater.complete()
                break

    def _convert_to_adk_message(self, message: AgentMessage) -> llm.Message:
        """Convert A2A message to ADK format."""
        parts = []
        for part in message.parts:
            if hasattr(part.root, 'text'):
                parts.append(llm.TextPart(text=part.root.text))
        return llm.Message(role=message.role, parts=parts)

    def _convert_to_a2a_parts(self, adk_parts) -> list[Part]:
        """Convert ADK parts to A2A format."""
        return [
            Part(root=TextPart(text=part.text))
            for part in (adk_parts or [])
            if hasattr(part, 'text')
        ]
```

### Step 5: Create Agent Instance

```python
# app/infrastructure/web/__init__.py
from a2a import Agent
from .rag_agent_executor import RagAgentExecutor

# Create executor
executor = RagAgentExecutor()

# Create A2A agent
agent = Agent(
    name="My ADK Agent",
    version="1.0.0",
    description="ADK agent exposed via A2A",
    executor=executor
)

__all__ = ["agent"]
```

### Step 6: Create A2A Server

```python
# app/main/a2a_main.py
import uvicorn
from a2a import A2A
from app.infrastructure.web import agent

def main():
    """Run A2A server."""
    a2a = A2A(agent)
    uvicorn.run(a2a, host="0.0.0.0", port=8006, log_level="info")

if __name__ == "__main__":
    main()
```

### Step 7: Update Client Code

```python
# Before (Direct ADK)
runner = Runner(tools=[...])
session = runner.create_session()
response = session.run(message)

# After (Via A2A Client)
client = A2AClient("http://localhost:8006")
await client.connect()
response = await client.send_message("Hello")
```

## Key Changes Summary

| Component | Before (ADK Only) | After (ADK + A2A) |
|-----------|------------------|-------------------|
| Entry Point | Direct Runner usage | A2A server via uvicorn |
| Communication | In-process | JSON-RPC over HTTP |
| Session Management | Manual | Handled by A2A |
| Response Format | ADK Event objects | A2A artifacts |
| Client | Direct Python calls | HTTP client |

## Testing the Migration

```bash
# 1. Start the server
python -m app.main.a2a_main

# 2. Test with curl
curl http://localhost:8006/.well-known/agent.json

# 3. Test with client
python -c "
import asyncio
from a2a_client import A2AClient

async def test():
    client = A2AClient()
    await client.connect()
    response = await client.send_message('Hello')
    print(f'Response: {response}')
    await client.close()

asyncio.run(test())
"
```

## Rollback Plan

If you need to rollback:
1. Keep original ADK code in a separate module
2. Use feature flags to switch between direct ADK and A2A
3. Maintain both entry points during transition

```python
# Dual mode support
if USE_A2A:
    # Run via A2A server
    uvicorn.run(A2A(agent), host="0.0.0.0", port=8006)
else:
    # Run direct ADK
    runner = Runner(tools=[...])
    # Original logic
```