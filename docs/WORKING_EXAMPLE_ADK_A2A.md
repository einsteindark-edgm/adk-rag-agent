# Working Example: ADK Agent with A2A Protocol

This is a complete working example based on the actual implementation in this project.

## Complete Working Implementation

### 1. Project Structure
```
my-adk-agent/
├── app/
│   ├── __init__.py
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── list_items.py
│   │   │   └── get_item_info.py
│   │   └── web/
│   │       ├── __init__.py
│   │       └── my_agent_executor.py
│   └── main/
│       ├── __init__.py
│       └── a2a_main.py
├── requirements.txt
├── .env
└── client.py
```

### 2. Requirements (requirements.txt)
```txt
google-adk==0.5.0
a2a-sdk>=0.2.11
uvicorn>=0.34.0
httpx>=0.27.0
python-dotenv==1.0.1
pydantic>=2.10.4
```

### 3. Simple ADK Tools

**app/infrastructure/tools/list_items.py**
```python
"""Tool for listing items."""

def list_items() -> dict:
    """List all available items.
    
    Returns:
        dict: List of items with status
    """
    # Simulate listing items
    items = [
        {"id": "1", "name": "Item 1", "status": "active"},
        {"id": "2", "name": "Item 2", "status": "active"},
    ]
    
    return {
        "status": "success",
        "message": f"Found {len(items)} items",
        "items": items
    }
```

**app/infrastructure/tools/get_item_info.py**
```python
"""Tool for getting item information."""

def get_item_info(item_id: str) -> dict:
    """Get information about a specific item.
    
    Args:
        item_id: The ID of the item
        
    Returns:
        dict: Item information
    """
    # Simulate getting item info
    if item_id == "1":
        return {
            "status": "success",
            "item": {
                "id": "1",
                "name": "Item 1",
                "description": "This is the first item",
                "created": "2025-01-01"
            }
        }
    
    return {
        "status": "error",
        "message": f"Item {item_id} not found"
    }
```

**app/infrastructure/tools/__init__.py**
```python
"""Infrastructure tools."""
from .list_items import list_items
from .get_item_info import get_item_info

__all__ = ["list_items", "get_item_info"]
```

### 4. The Executor (MOST IMPORTANT PART)

**app/infrastructure/web/my_agent_executor.py**
```python
"""Agent executor that bridges ADK with A2A protocol."""

import logging
from typing import AsyncIterator

from google.adk import llm
from google.adk.common import event
from google.adk.runner import Runner

from a2a import (
    Executor, 
    AgentMessage, 
    ToolCallSpec, 
    TaskContext, 
    TaskUpdater,
    Part,
    TextPart,
    TaskState
)

logger = logging.getLogger(__name__)

class MyAgentExecutor(Executor):
    """Executor implementation for ADK agent."""

    def __init__(self):
        """Initialize the executor with ADK runner."""
        # Import tools
        from ..tools import list_items, get_item_info
        
        # Create ADK runner
        self.runner = Runner(
            tools=[list_items, get_item_info],
            system_instruction="""You are a helpful assistant that can list items and get information about them.
            
Available tools:
- list_items: Lists all available items
- get_item_info: Gets detailed information about a specific item

Always use these tools to answer questions about items."""
        )
        logger.info("MyAgentExecutor initialized with tools: list_items, get_item_info")

    async def execute(
        self,
        *,
        session_id: str,
        messages: list[AgentMessage],
        context: TaskContext,
        tool_specs: list[ToolCallSpec],
        updater: TaskUpdater | None = None,
    ) -> None:
        """Execute the agent request.
        
        This is called by the A2A server for each user message.
        """
        logger.info(f"=== Starting execution for session {session_id} ===")
        
        if not messages:
            logger.warning("No messages provided")
            return

        # Get the latest user message
        latest_message = messages[-1]
        logger.debug(f"Processing message: {latest_message}")
        
        # Convert A2A message to ADK format
        adk_message = self._convert_a2a_to_adk_message(latest_message)
        
        # IMPORTANT: These are SYNCHRONOUS - no await!
        session = self.runner.get_session(session_id)
        if not session:
            logger.info(f"Creating new session: {session_id}")
            session = self.runner.create_session(session_id=session_id)
        else:
            logger.info(f"Using existing session: {session_id}")
        
        # IMPORTANT: TaskUpdater methods are ASYNCHRONOUS - use await!
        if not context.current_task:
            logger.debug("Submitting new task")
            await updater.submit()
            
        logger.debug("Starting work")
        await updater.start_work()

        # Run the ADK agent
        logger.info("Running ADK agent...")
        async for event in session.run_async(adk_message):
            logger.debug(f"Received event: {type(event)}")
            
            if event.is_final_response():
                # Final response - convert and send
                logger.info("Got final response from agent")
                parts = self._convert_genai_to_a2a_parts(
                    event.content.parts if event.content and event.content.parts else []
                )
                
                # Add as artifact and complete
                await updater.add_artifact(parts)
                await updater.complete()
                logger.info("Task completed")
                break
                
            elif not event.get_function_calls():
                # Intermediate update (thinking, etc.)
                logger.debug("Sending intermediate update")
                parts = self._convert_genai_to_a2a_parts(
                    event.content.parts if event.content and event.content.parts else []
                )
                await updater.update_status(
                    TaskState.working,
                    message=updater.new_agent_message(parts)
                )

    def _convert_a2a_to_adk_message(self, message: AgentMessage) -> llm.Message:
        """Convert A2A message format to ADK format."""
        parts = []
        
        for part in message.parts:
            if hasattr(part.root, 'text'):
                parts.append(llm.TextPart(text=part.root.text))
                
        return llm.Message(
            role=message.role,
            parts=parts
        )

    def _convert_genai_to_a2a_parts(self, genai_parts: list) -> list[Part]:
        """Convert GenAI/ADK parts to A2A format."""
        a2a_parts = []
        
        for part in genai_parts:
            if hasattr(part, 'text') and part.text:
                a2a_parts.append(Part(root=TextPart(text=part.text)))
                
        return a2a_parts
```

### 5. Agent Configuration

**app/infrastructure/web/__init__.py**
```python
"""Web infrastructure for the agent."""

from a2a import Agent as A2AAgent
from .my_agent_executor import MyAgentExecutor

# Create executor instance
executor = MyAgentExecutor()

# Create A2A agent
agent = A2AAgent(
    name="My ADK Agent",
    version="1.0.0",
    description="An example ADK agent exposed via A2A protocol",
    executor=executor
)

__all__ = ["agent", "executor"]
```

### 6. A2A Server Entry Point

**app/main/a2a_main.py**
```python
"""A2A server entry point."""

import logging
import uvicorn
from a2a import A2A
from app.infrastructure.web import agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Run the A2A server."""
    # Create A2A app with our agent
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

### 7. Client Implementation

**client.py**
```python
"""Client for testing the ADK agent via A2A."""

import asyncio
import sys
import uuid
import httpx

class AgentClient:
    """Client for A2A agent communication."""
    
    def __init__(self, agent_url: str = "http://localhost:8006"):
        self.agent_url = agent_url
        self.httpx_client = httpx.AsyncClient(timeout=30.0)
        self.session_id = f"session-{uuid.uuid4().hex[:8]}"
        self.connected = False
    
    async def connect(self):
        """Connect to the agent."""
        try:
            response = await self.httpx_client.get(
                f"{self.agent_url}/.well-known/agent.json"
            )
            if response.status_code == 200:
                agent_info = response.json()
                print(f"✅ Connected to {agent_info['name']} v{agent_info['version']}")
                self.connected = True
            else:
                raise Exception(f"Failed to connect: {response.status_code}")
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            raise
    
    async def send_message(self, message: str) -> str:
        """Send message and get response."""
        if not self.connected:
            await self.connect()
        
        # Create JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "message/send",
            "params": {
                "message": {
                    "messageId": str(uuid.uuid4()),
                    "role": "user",
                    "parts": [{"text": message}]
                },
                "sessionId": self.session_id
            }
        }
        
        try:
            response = await self.httpx_client.post(
                self.agent_url,
                json=request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if "result" in result:
                    return self._extract_text(result["result"])
                elif "error" in result:
                    return f"Error: {result['error'].get('message', 'Unknown')}"
            
            return f"HTTP Error {response.status_code}"
            
        except Exception as e:
            return f"Request failed: {e}"
    
    def _extract_text(self, result):
        """Extract text from response."""
        if isinstance(result, dict) and "artifacts" in result:
            texts = []
            for artifact in result["artifacts"]:
                if "parts" in artifact:
                    for part in artifact["parts"]:
                        if "text" in part:
                            texts.append(part["text"])
            return "\n".join(texts) if texts else "No response"
        return "No response found"
    
    async def close(self):
        """Close client."""
        await self.httpx_client.aclose()

async def main():
    """Test the agent."""
    client = AgentClient()
    
    try:
        await client.connect()
        print("\nType 'exit' to quit\n")
        
        # Test messages
        test_messages = [
            "List all items",
            "Get information about item 1",
            "Get information about item 99"
        ]
        
        for msg in test_messages:
            print(f"You: {msg}")
            response = await client.send_message(msg)
            print(f"Agent: {response}\n")
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    print("🚀 ADK Agent Client Test")
    print("Make sure server is running: python -m app.main.a2a_main\n")
    asyncio.run(main())
```

### 8. Running the Example

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the A2A server
python -m app.main.a2a_main

# 3. In another terminal, run the client
python client.py
```

### Expected Output

**Server:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8006
```

**Client:**
```
🚀 ADK Agent Client Test
Make sure server is running: python -m app.main.a2a_main

✅ Connected to My ADK Agent v1.0.0

You: List all items
Agent: I found 2 items:
1. Item 1 - active
2. Item 2 - active

You: Get information about item 1
Agent: Here's the information about Item 1:
- ID: 1
- Name: Item 1
- Description: This is the first item
- Created: 2025-01-01

You: Get information about item 99
Agent: I couldn't find item 99. It appears this item doesn't exist.
```

## Key Points from This Working Example

1. **ADK Methods**: Remember which are sync vs async
   - `runner.get_session()` - SYNC
   - `runner.create_session()` - SYNC  
   - `updater.submit()` - ASYNC
   - `updater.start_work()` - ASYNC
   - `updater.add_artifact()` - ASYNC
   - `updater.complete()` - ASYNC

2. **Message Conversion**: Always check if attributes exist
3. **Response Format**: Extract from `result['artifacts'][0]['parts'][0]['text']`
4. **Tools**: Must be imported in executor's `__init__`
5. **Logging**: Essential for debugging the async flow

This example can be extended with more tools and complex logic while maintaining the same structure.