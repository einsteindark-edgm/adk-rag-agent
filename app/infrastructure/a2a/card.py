from a2a.types import AgentCard, AgentCapabilities, AgentSkill

def get_agent_card() -> AgentCard:
    """Get the agent card for our RAG agent.
    
    CRITICAL: This metadata is served at /.well-known/agent.json
    and tells other agents what we can do.
    """
    return AgentCard(
        # Basic metadata
        name="Vertex AI RAG Agent",
        description="AI agent for managing and querying Vertex AI RAG corpora",
        version="1.0.0",
        url="http://localhost:8080/",
        
        # Input/output modes
        defaultInputModes=["text/plain"],
        defaultOutputModes=["text/plain"],
        
        # Capabilities
        capabilities=AgentCapabilities(
            streaming=True,
            multimodal=True,
            customMetadata={
                "supported_operations": [
                    "query_corpus",
                    "list_corpora", 
                    "create_corpus",
                    "add_documents",
                    "get_corpus_info",
                    "delete_document",
                    "delete_corpus"
                ],
                "llm_model": "gemini-2.0-flash-exp",
                "rag_backend": "vertex-ai"
            }
        ),
        
        # Skills
        skills=[
            AgentSkill(
                id="rag_query",
                name="RAG Query",
                description="Query documents from Vertex AI RAG corpus",
                tags=["rag", "search", "retrieval"],
                examples=[
                    "Search for information about Clean Architecture",
                    "What documents are available in the corpus?",
                    "Find information about agent protocols"
                ]
            ),
            AgentSkill(
                id="corpus_management",
                name="Corpus Management",
                description="Manage Vertex AI RAG corpora - create, list, delete",
                tags=["rag", "corpus", "management"],
                examples=[
                    "List all available corpora",
                    "Create a new corpus named 'technical-docs'",
                    "Get information about corpus '123456'"
                ]
            ),
            AgentSkill(
                id="document_management",
                name="Document Management",
                description="Add and remove documents from RAG corpora",
                tags=["rag", "documents", "ingestion"],
                examples=[
                    "Add this PDF to the corpus",
                    "Remove document XYZ from the corpus",
                    "Import all markdown files from this folder"
                ]
            )
        ]
    )