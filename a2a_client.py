"""Test client for Vertex AI RAG Agent using A2A protocol."""
import asyncio
import sys
import json
import uuid
from typing import Optional
import httpx
from a2a.types import Part, TextPart


class RAGAgentClient:
    """Client for interacting with Colombian Import Specialist via A2A protocol."""
    
    def __init__(self, agent_url: str = "http://localhost:8006"):
        """Initialize with agent URL.
        
        DEFAULT: Assumes A2A server at localhost:8006
        """
        self.agent_url = agent_url
        self.httpx_client = httpx.AsyncClient(timeout=30.0)
        self.connected = False
        self.session_id = f"session-{uuid.uuid4().hex[:8]}"
    
    async def connect(self):
        """Connect to the agent."""
        try:
            # Check if agent is available
            response = await self.httpx_client.get(f"{self.agent_url}/.well-known/agent.json")
            if response.status_code == 200:
                agent_info = response.json()
                print(f"✅ Connected to {agent_info['name']} v{agent_info['version']}")
                self.connected = True
            else:
                raise Exception(f"Failed to connect: {response.status_code}")
        except Exception as e:
            print(f"❌ Failed to connect to agent: {e}")
            raise
    
    async def send_message(self, message: str) -> str:
        """Send a message to the agent and get response.
        
        Args:
            message: Natural language message
            
        Returns:
            Agent's response as string
        """
        if not self.connected:
            await self.connect()
        
        # Create JSON-RPC request using the correct format
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
                            "text": message  # Direct text field, not root.text
                        }
                    ]
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
                    # Extract text from result
                    return self._extract_text_from_result(result["result"])
                elif "error" in result:
                    return f"Error: {result['error'].get('message', 'Unknown error')}"
                else:
                    return f"Unexpected response format"
            else:
                return f"HTTP Error {response.status_code}"
                
        except Exception as e:
            return f"Request failed: {e}"
    
    def _extract_text_from_result(self, result):
        """Extract text from the JSON-RPC result."""
        try:
            if isinstance(result, dict):
                # Look for artifacts (the actual response format)
                if "artifacts" in result and result["artifacts"]:
                    texts = []
                    for artifact in result["artifacts"]:
                        if "parts" in artifact:
                            for part in artifact["parts"]:
                                if "text" in part:
                                    texts.append(part["text"])
                                elif "kind" in part and part["kind"] == "text" and "text" in part:
                                    texts.append(part["text"])
                    if texts:
                        return "\n".join(texts)
                
                # Look for message content (alternative format)
                if "message" in result and "parts" in result["message"]:
                    parts = result["message"]["parts"]
                    texts = []
                    for part in parts:
                        if "text" in part:
                            texts.append(part["text"])
                    if texts:
                        return "\n".join(texts)
                
                # Look for direct content
                for field in ["content", "response", "text"]:
                    if field in result:
                        return str(result[field])
                
                # If nothing found but there's a status
                if "status" in result and "state" in result["status"]:
                    if result["status"]["state"] == "completed":
                        return "Task completed but no text response available"
            
            return "No response text found"
            
        except Exception as e:
            return f"Error extracting response: {e}"
    
    async def close(self):
        """Close the client connection."""
        self.connected = False
        await self.httpx_client.aclose()


class RAGAgentInteraction:
    """Handles interaction with the RAG Agent."""
    
    def __init__(self, agent_url: str = "http://localhost:8006"):
        """Initialize with agent URL."""
        self.client = RAGAgentClient(agent_url)
    
    async def interactive_session(self):
        """Run interactive session with the agent.
        
        INTERACTIVE: User types messages, sees responses.
        """
        print("🔗 Connecting to RAG agent...")
        
        try:
            await self.client.connect()
            print("✅ Connected! Type 'exit' to quit.\n")
            
            while True:
                # Get user input
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['exit', 'quit']:
                    break
                
                if not user_input:
                    continue
                
                # Send to agent
                print("Agent: ", end="", flush=True)
                response = await self.client.send_message(user_input)
                print(response)
                print()  # Empty line for readability
                
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await self.client.close()
    
    async def run_tests(self):
        """Run automated tests.
        
        AUTOMATED: Tests common import query scenarios.
        """
        test_messages = [
            "List all available corpora",
            "Create the import_export corpus if it doesn't exist",
            "What are the requirements for importing textiles to Colombia?",
            "What documents do I need to import electronics?",
            "Are there restrictions on importing used vehicles?",
            "What are the import duties for machinery?",
            "What is the customs clearance process in Colombia?"
        ]
        
        try:
            await self.client.connect()
            print("✅ Connected to agent\n")
            
            for msg in test_messages:
                print(f"📝 Test: {msg}")
                response = await self.client.send_message(msg)
                print(f"✅ Response: {response}\n")
                await asyncio.sleep(1)  # Rate limiting
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
        finally:
            await self.client.close()


async def main():
    """Main entry point for test client.
    
    USAGE:
    - python3 a2a_client.py          # Interactive mode
    - python3 a2a_client.py --test   # Run automated tests
    """
    interaction = RAGAgentInteraction()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Run automated tests
        await interaction.run_tests()
    else:
        # Run interactive session
        await interaction.interactive_session()


if __name__ == "__main__":
    print("🚢 Colombian Import Specialist Client (A2A)")
    print("Make sure the A2A server is running: python -m app.main.a2a_main")
    print("Run with --test flag for automated tests\n")
    print("Note: Ensure the 'import_export' corpus exists with 'rules_imports' document")
    print("for accurate import regulation responses.\n")
    
    asyncio.run(main())