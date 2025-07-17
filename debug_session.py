#!/usr/bin/env python
"""Debug script to understand the session creation issue."""

import asyncio
import logging
from google.adk.runners import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService
from app.infrastructure.agent import root_agent

logging.basicConfig(level=logging.DEBUG)

async def test_session_creation():
    """Test session creation to understand the issue."""
    
    # Create runner
    runner = Runner(
        app_name="Test",
        agent=root_agent,
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )
    
    print("Testing session service methods...")
    
    # Test get_session
    print("\n1. Testing get_session:")
    result = runner.session_service.get_session(
        app_name="Test",
        user_id="test_user",
        session_id="test_session"
    )
    print(f"   Type: {type(result)}")
    print(f"   Value: {result}")
    
    # Test create_session
    print("\n2. Testing create_session:")
    result = runner.session_service.create_session(
        app_name="Test",
        user_id="test_user",
        session_id="test_session"
    )
    print(f"   Type: {type(result)}")
    print(f"   Is coroutine: {asyncio.iscoroutine(result)}")
    
    if asyncio.iscoroutine(result):
        print("   Awaiting coroutine...")
        session = await result
        print(f"   After await - Type: {type(session)}")
        print(f"   After await - Has id: {hasattr(session, 'id')}")
        if hasattr(session, 'id'):
            print(f"   Session ID: {session.id}")
    else:
        print(f"   Has id: {hasattr(result, 'id')}")
        if hasattr(result, 'id'):
            print(f"   Session ID: {result.id}")

if __name__ == "__main__":
    asyncio.run(test_session_creation())