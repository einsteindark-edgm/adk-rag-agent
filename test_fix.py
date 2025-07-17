#!/usr/bin/env python
"""Quick test to verify the async fix works."""

import asyncio
from a2a_client import RAGAgentClient

async def test():
    client = RAGAgentClient()
    
    try:
        await client.connect()
        print("✅ Connected successfully\n")
        
        # Test a simple query
        response = await client.send_message("Hello, can you help me with import procedures?")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test())