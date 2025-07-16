# Troubleshooting Guide: ADK + A2A Integration

## Error Reference with Actual Solutions

### 1. A2AClient Initialization Error

**Error Message:**
```
TypeError: A2AClient.__init__() missing 1 required positional argument: 'httpx_client'
```

**Root Cause:** The a2a-sdk API changed between versions. Older examples show passing httpx_client.

**Solution:**
```python
# ❌ WRONG (Old API)
import httpx
httpx_client = httpx.AsyncClient()
client = A2AClient(agent_url, httpx_client)

# ✅ CORRECT (Current API)
client = A2AClient(agent_url)  # httpx_client created internally
```

### 2. Package Installation Error

**Error Message:**
```
ERROR: Could not find a version that satisfies the requirement a2a==0.1.0
```

**Root Cause:** Wrong package name. The correct package is `a2a-sdk`, not `a2a`.

**Solution:**
```txt
# ❌ WRONG
a2a==0.1.0

# ✅ CORRECT
a2a-sdk>=0.2.11
```

### 3. Await Expression Error

**Error Message:**
```
"object NoneType can't be used in 'await' expression"
```

**Root Cause:** Trying to await synchronous ADK methods.

**Investigation Steps:**
1. Check ADK source code to verify which methods are sync/async
2. Look at method signatures - async methods have `async def`

**Solution:**
```python
# ❌ WRONG
session = await self.runner.get_session(session_id)  # get_session is SYNC
session = await self.runner.create_session(session_id=session_id)  # create_session is SYNC

# ✅ CORRECT
session = self.runner.get_session(session_id)  # No await
session = self.runner.create_session(session_id=session_id)  # No await

# But TaskUpdater methods ARE async:
await updater.submit()  # Correct - needs await
await updater.start_work()  # Correct - needs await
await updater.add_artifact(parts)  # Correct - needs await
await updater.complete()  # Correct - needs await
```

### 4. Response Parsing Error

**Error Message:**
```
Agent: Error: Request failed: ...
```

**Root Cause:** Client shows "Request failed" even though server processed successfully.

**Investigation:**
```python
# Check raw response structure
print(f"Raw response: {response.json()}")
```

**Actual Response Structure:**
```json
{
  "id": "request-id",
  "jsonrpc": "2.0",
  "result": {
    "artifacts": [
      {
        "artifactId": "artifact-id",
        "parts": [
          {
            "kind": "text",
            "text": "The actual response text"
          }
        ]
      }
    ],
    "status": {
      "state": "completed"
    }
  }
}
```

**Solution:**
```python
def _extract_text_from_result(self, result):
    """Extract text from the JSON-RPC result."""
    if isinstance(result, dict):
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
```

### 5. Import Path Errors

**Error Message:**
```
ImportError: cannot import name 'tool1' from 'app.infrastructure.tools'
```

**Root Cause:** Missing `__init__.py` files or incorrect import paths.

**Solution:**
```python
# app/infrastructure/tools/__init__.py
from .tool1 import tool1
from .tool2 import tool2

__all__ = ["tool1", "tool2"]
```

## Debugging Techniques

### 1. Enable Comprehensive Logging

```python
import logging

# Configure all relevant loggers
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('app.infrastructure').setLevel(logging.DEBUG)
logging.getLogger('google.adk').setLevel(logging.DEBUG)
logging.getLogger('a2a').setLevel(logging.DEBUG)
logging.getLogger('httpx').setLevel(logging.DEBUG)
```

### 2. Trace Request Flow

Add logging at each step:
```python
logger.info("=== Starting operation ===")
logger.debug(f"Session ID: {session_id}")
logger.debug(f"Message: {messages[-1]}")
logger.info("Converting message to ADK format...")
logger.info("Running ADK agent...")
logger.info("Converting response to A2A format...")
logger.info("=== Operation completed ===")
```

### 3. Verify Tool Registration

```python
# In executor __init__
logger.info(f"Registered tools: {[t.__name__ for t in self.runner.tools]}")
```

### 4. Check Session State

```python
session = self.runner.get_session(session_id)
logger.info(f"Session exists: {session is not None}")
if session:
    logger.debug(f"Session ID: {session.session_id}")
```

### 5. Test Components Individually

```python
# Test 1: Direct ADK runner
runner = Runner(tools=[...])
session = runner.create_session()
# Verify this works before adding A2A

# Test 2: A2A server health
curl http://localhost:8080/.well-known/agent.json

# Test 3: Simple message
response = await client.send_message("Hello")
```

## Common Patterns That Cause Issues

### 1. Mixing Sync/Async Incorrectly

```python
# This pattern causes issues:
async def some_method(self):
    session = await self.runner.get_session(...)  # ❌ WRONG - sync method
    await updater.complete()  # ✅ CORRECT - async method
```

### 2. Not Handling Empty Responses

```python
# Always check for content
if event.content and event.content.parts:
    parts = event.content.parts
else:
    parts = []
```

### 3. Incorrect Message Conversion

```python
# Always check part structure
for part in message.parts:
    if hasattr(part.root, 'text'):  # Check attribute exists
        # Process text part
```

## Quick Diagnosis Checklist

- [ ] Is the A2A server running? Check with `curl http://localhost:8080/.well-known/agent.json`
- [ ] Are all dependencies installed? Check `pip list | grep -E "a2a-sdk|google-adk"`
- [ ] Are tools properly imported? Check executor's `_get_tools()` method
- [ ] Is logging enabled? Add `logging.basicConfig(level=logging.DEBUG)`
- [ ] Is the session being created? Log `session is not None`
- [ ] Are responses being extracted correctly? Log raw response structure
- [ ] Are async/sync methods used correctly? No await on sync ADK methods

## Emergency Fixes

### Server Won't Start
```bash
# Check port availability
lsof -i :8080

# Try different port
uvicorn.run(a2a, host="0.0.0.0", port=8081)
```

### Client Can't Connect
```python
# Add timeout and retry
client = A2AClient()
for i in range(3):
    try:
        await client.connect()
        break
    except Exception as e:
        print(f"Retry {i+1}: {e}")
        await asyncio.sleep(1)
```

### Response Timeout
```python
# Increase timeout for long operations
self.httpx_client = httpx.AsyncClient(timeout=60.0)  # 60 seconds
```