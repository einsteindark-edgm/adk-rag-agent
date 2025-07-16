# ADK + A2A Quick Reference

## Essential Code Snippets

### 1. Minimal A2A Server Setup
```python
# app/main/a2a_main.py
import uvicorn
from a2a import A2A
from app.infrastructure.web import agent

uvicorn.run(A2A(agent), host="0.0.0.0", port=8006)
```

### 2. Agent Definition
```python
# app/infrastructure/web/__init__.py
from a2a import Agent
from .rag_agent_executor import RagAgentExecutor

executor = RagAgentExecutor()
agent = Agent(
    name="My Agent",
    version="1.0.0", 
    description="Agent description",
    executor=executor
)
```

### 3. Executor Core Pattern
```python
# app/infrastructure/web/rag_agent_executor.py
from a2a import Executor
from google.adk.runner import Runner

class RagAgentExecutor(Executor):
    def __init__(self):
        self.runner = Runner(tools=[...])
    
    async def execute(self, *, session_id, messages, context, tool_specs, updater):
        # Key steps:
        # 1. Get/create ADK session (SYNC)
        session = self.runner.get_session(session_id) or self.runner.create_session(session_id=session_id)
        
        # 2. Update task status (ASYNC)
        await updater.submit()
        await updater.start_work()
        
        # 3. Run ADK agent
        async for event in session.run_async(message):
            if event.is_final_response():
                await updater.add_artifact(parts)
                await updater.complete()
                break
```

### 4. Client Request Format
```python
# JSON-RPC request structure
{
    "jsonrpc": "2.0",
    "id": "unique-id",
    "method": "message/send",
    "params": {
        "message": {
            "messageId": "msg-id",
            "role": "user",
            "parts": [{"text": "user message"}]
        },
        "sessionId": "session-id"
    }
}
```

### 5. Response Extraction
```python
# Response structure
response = {
    "result": {
        "artifacts": [{
            "parts": [{
                "text": "agent response"
            }]
        }]
    }
}

# Extract text
text = response["result"]["artifacts"][0]["parts"][0]["text"]
```

## Critical Points to Remember

### ✅ DO:
- Use `a2a-sdk>=0.2.11` (not `a2a==0.1.0`)
- await TaskUpdater methods: `submit()`, `start_work()`, `add_artifact()`, `complete()`
- Create httpx client inside A2AClient
- Extract response from `result.artifacts[0].parts[0].text`
- Check if session exists before creating

### ❌ DON'T:
- Don't await `runner.get_session()` or `runner.create_session()` - they're SYNC
- Don't pass httpx_client to A2AClient constructor
- Don't assume all ADK methods are async
- Don't forget to call `updater.complete()` after final response

## Debug Commands

```bash
# Check server health
curl http://localhost:8006/.well-known/agent.json

# Run server
python -m app.main.a2a_main

# Test client
python a2a_client.py
```

## Common Fixes

| Error | Fix |
|-------|-----|
| `TypeError: A2AClient.__init__() missing 1 required positional argument` | Don't pass httpx_client |
| `object NoneType can't be used in 'await' expression` | Don't await sync ADK methods |
| `ERROR: Could not find a version that satisfies the requirement a2a==0.1.0` | Use `a2a-sdk>=0.2.11` |
| Response shows full JSON | Extract from `artifacts[0].parts[0].text` |