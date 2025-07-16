import asyncio
import logging
from collections.abc import AsyncGenerator

from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    FilePart,
    FileWithBytes,
    FileWithUri,
    Part,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils.errors import ServerError
from google.adk.runners import Runner
from google.adk.events import Event
from google.genai import types

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class RAGAgentExecutor(AgentExecutor):
    """An AgentExecutor that runs the RAG ADK-based Agent.
    
    CRITICAL: This executor uses Google ADK Runner to execute
    the agent asynchronously with proper event handling.
    """

    def __init__(self, runner: Runner):
        self.runner = runner
        self._running_sessions = {}

    def _run_agent(
        self, session_id: str, new_message: types.Content
    ) -> AsyncGenerator[Event, None]:
        """Run the ADK agent asynchronously.
        
        RUNNER: Uses ADK Runner to execute the agent with session management.
        """
        logger.debug(f"_run_agent called with session_id={session_id}")
        # Note: Despite being called run_async, this method returns an AsyncGenerator directly
        # not a coroutine that needs to be awaited
        return self.runner.run_async(
            session_id=session_id, 
            user_id="rag_agent_user", 
            new_message=new_message
        )

    async def _process_request(
        self,
        new_message: types.Content,
        session_id: str,
        task_updater: TaskUpdater,
    ) -> None:
        """Process the request through the ADK agent.
        
        EVENT HANDLING: Processes events from the agent execution
        and updates the task status accordingly.
        """
        # Ensure session exists
        session_obj = await self._upsert_session(session_id)
        session_id = session_obj.id

        # Run the agent and process events
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
                            event.content.parts
                            if event.content and event.content.parts
                            else []
                        ),
                    ),
                )
            else:
                # Function call event - just log it
                logger.debug("Processing function call event")

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ):
        """Execute the A2A task using ADK agent.
        
        MAIN ENTRY: Called by A2A when a message is received.
        """
        logger.debug("RAGAgentExecutor.execute called")
        logger.debug(f"Context: task_id={context.task_id}, context_id={context.context_id}")
        
        if not context.task_id or not context.context_id:
            raise ValueError("RequestContext must have task_id and context_id")
        if not context.message:
            raise ValueError("RequestContext must have a message")

        # Create task updater
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        
        # Submit new task if needed
        if not context.current_task:
            await updater.submit()
            
        # Start work
        await updater.start_work()
        
        # Process the request
        await self._process_request(
            types.UserContent(
                parts=self._convert_a2a_parts_to_genai(context.message.parts),
            ),
            context.context_id,
            updater,
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        """Cancel is not supported."""
        raise ServerError(error=UnsupportedOperationError())

    async def _upsert_session(self, session_id: str):
        """Get or create a session for the conversation."""
        session = self.runner.session_service.get_session(
            app_name=self.runner.app_name, 
            user_id="rag_agent_user", 
            session_id=session_id
        )
        if session is None:
            session = self.runner.session_service.create_session(
                app_name=self.runner.app_name,
                user_id="rag_agent_user",
                session_id=session_id,
            )
        if session is None:
            raise RuntimeError(f"Failed to get or create session: {session_id}")
        return session

    def _convert_a2a_parts_to_genai(self, parts: list[Part]) -> list[types.Part]:
        """Convert A2A parts to GenAI parts."""
        return [self._convert_a2a_part_to_genai(part) for part in parts]

    def _convert_a2a_part_to_genai(self, part: Part) -> types.Part:
        """Convert a single A2A part to GenAI part.
        
        CRITICAL: Handles text and file parts for complete compatibility.
        """
        root = part.root
        if isinstance(root, TextPart):
            return types.Part(text=root.text)
        if isinstance(root, FilePart):
            if isinstance(root.file, FileWithUri):
                return types.Part(
                    file_data=types.FileData(
                        file_uri=root.file.uri, 
                        mime_type=root.file.mimeType
                    )
                )
            if isinstance(root.file, FileWithBytes):
                return types.Part(
                    inline_data=types.Blob(
                        data=root.file.bytes.encode("utf-8"),
                        mime_type=root.file.mimeType or "application/octet-stream",
                    )
                )
            raise ValueError(f"Unsupported file type: {type(root.file)}")
        raise ValueError(f"Unsupported part type: {type(part)}")

    def _convert_genai_parts_to_a2a(self, parts: list[types.Part]) -> list[Part]:
        """Convert GenAI parts to A2A parts."""
        return [
            self._convert_genai_part_to_a2a(part)
            for part in parts
            if (part.text or part.file_data or part.inline_data)
        ]

    def _convert_genai_part_to_a2a(self, part: types.Part) -> Part:
        """Convert a single GenAI part to A2A part.
        
        CRITICAL: Handles all GenAI part types for complete compatibility.
        """
        if part.text:
            return Part(root=TextPart(text=part.text))
        if part.file_data:
            if not part.file_data.file_uri:
                raise ValueError("File URI is missing")
            return Part(
                root=FilePart(
                    file=FileWithUri(
                        uri=part.file_data.file_uri,
                        mimeType=part.file_data.mime_type,
                    )
                )
            )
        if part.inline_data:
            if not part.inline_data.data:
                raise ValueError("Inline data is missing")
            return Part(
                root=FilePart(
                    file=FileWithBytes(
                        bytes=part.inline_data.data.decode("utf-8"),
                        mimeType=part.inline_data.mime_type,
                    )
                )
            )
        raise ValueError(f"Unsupported part type: {part}")