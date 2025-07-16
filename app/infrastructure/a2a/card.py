from a2a.types import AgentCard, AgentCapabilities, AgentSkill

def get_agent_card() -> AgentCard:
    """Get the agent card for our Colombian Import Specialist agent.
    
    CRITICAL: This metadata is served at /.well-known/agent.json
    and tells other agents what we can do.
    """
    return AgentCard(
        # Basic metadata
        name="Colombian Import Specialist",
        description="AI agent specialized in Colombian import procedures and regulations",
        version="1.0.0",
        url="http://localhost:8006/",
        
        # Input/output modes
        defaultInputModes=["text/plain"],
        defaultOutputModes=["text/plain"],
        
        # Capabilities
        capabilities=AgentCapabilities(
            streaming=True,
            multimodal=True,
            customMetadata={
                "supported_operations": [
                    "query_import_regulations",
                    "get_import_requirements",
                    "check_restricted_items",
                    "calculate_tariffs",
                    "list_required_documents",
                    "corpus_management"
                ],
                "llm_model": "gemini-2.0-flash-exp",
                "rag_backend": "vertex-ai",
                "specialization": "colombian_imports",
                "primary_corpus": "import_export",
                "primary_document": "rules_imports"
            }
        ),
        
        # Skills
        skills=[
            AgentSkill(
                id="import_requirements",
                name="Import Requirements",
                description="Get requirements for importing specific products to Colombia",
                tags=["imports", "requirements", "colombia", "customs"],
                examples=[
                    "What are the requirements for importing textiles to Colombia?",
                    "What documents do I need to import electronics?",
                    "What permits are required for importing food products?"
                ]
            ),
            AgentSkill(
                id="tariffs_taxes",
                name="Tariffs and Taxes",
                description="Information about import duties, VAT, and other taxes for Colombia",
                tags=["tariffs", "taxes", "duties", "colombia"],
                examples=[
                    "What are the import duties for machinery?",
                    "How is VAT calculated on imports?",
                    "What is the tariff for importing vehicles?"
                ]
            ),
            AgentSkill(
                id="restricted_items",
                name="Restricted Items",
                description="Check restrictions and prohibitions for importing to Colombia",
                tags=["restrictions", "prohibited", "colombia", "regulations"],
                examples=[
                    "Is it legal to import used clothing to Colombia?",
                    "What items are prohibited for import?",
                    "Are there restrictions on importing chemicals?"
                ]
            ),
            AgentSkill(
                id="customs_procedures",
                name="Customs Procedures",
                description="Step-by-step customs clearance procedures for Colombia",
                tags=["customs", "procedures", "clearance", "colombia"],
                examples=[
                    "What is the customs clearance process?",
                    "How long does customs clearance take?",
                    "What are the steps for import declaration?"
                ]
            )
        ]
    )