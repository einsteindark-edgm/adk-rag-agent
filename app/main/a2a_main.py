import asyncio
import logging
from uvicorn import Config, Server

from app.infrastructure.a2a import get_agent_card
from app.infrastructure.web.rag_agent_executor import RAGAgentExecutor
from app.infrastructure.config import settings
from app.infrastructure.agent import root_agent

# CRITICAL: Import A2A components
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore

# CRITICAL: Import ADK components for Runner
from google.adk.runners import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_a2a_app():
    """Create A2A application with ADK Runner integration.
    
    CRITICAL STEPS:
    1. Create ADK Runner with agent
    2. Create executor with Runner
    3. Create A2A handler
    4. Create A2A application
    """
    # Get agent card
    agent_card = get_agent_card()
    
    # Create ADK Runner
    # RUNNER: Manages agent execution with sessions and memory
    runner = Runner(
        app_name=agent_card.name,
        agent=root_agent,
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )
    
    # Create executor with Runner
    # EXECUTOR: Bridges A2A protocol with ADK agent
    agent_executor = RAGAgentExecutor(runner)
    
    # Create A2A handler with executor
    # HANDLER: Manages A2A protocol and tasks
    handler = DefaultRequestHandler(
        agent_executor=agent_executor,
        task_store=InMemoryTaskStore(),
    )
    
    # Create A2A application
    # FRAMEWORK: Starlette-based ASGI application
    app = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=handler
    )
    
    return app

def run_server():
    """Run the A2A server synchronously."""
    asyncio.run(_run_server_async())

async def _run_server_async():
    """Run the A2A server with proper lifecycle management.
    
    LIFECYCLE:
    1. Create A2A app with ADK Runner
    2. Start server
    3. Handle shutdown gracefully
    """
    try:
        logger.info("🚢 Starting Colombian Import Specialist Server...")
        
        # Create app
        app = create_a2a_app()
        
        # Configure server
        # CRITICAL: Using port 8006 for A2A server
        config = Config(
            app=app.build(),  # Note: A2AStarletteApplication.build() returns the ASGI app
            host=settings.HOST,  # Default: 0.0.0.0
            port=settings.PORT,  # Default: 8006
            log_level="info"
        )
        
        server = Server(config)
        
        # Run server
        logger.info(f"🌟 Colombian Import Specialist running at http://{settings.HOST}:{settings.PORT}")
        logger.info("📄 Agent card available at /.well-known/agent.json")
        logger.info("📦 Primary corpus: import_export | Primary document: rules_imports")
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise