from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from app.infrastructure.config import settings

def get_agent_card() -> AgentCard:
    """Get the agent card for Customer Communication Agent.
    
    This agent specializes in communicating with customers about
    shipment anomalies, delays, and ETA updates with appropriate
    tone awareness.
    """
    return AgentCard(
        # Basic metadata
        name="Customer Communication Agent",
        description="AI agent specialized in customer communication for shipment tracking and anomaly updates. Provides tone-aware, professional responses about delays, ETAs, and shipment status.",
        version="1.0.0",
        url="http://localhost:8006/",
        
        # Input/output modes
        defaultInputModes=["text/plain"],
        defaultOutputModes=["text/plain"],
        
        # Capabilities
        capabilities=AgentCapabilities(
            streaming=True,
            multimodal=False,
            customMetadata={
                "supported_operations": [
                    "check_shipment_status",
                    "explain_delay_reason", 
                    "provide_new_eta",
                    "handle_customer_inquiry",
                    "generate_status_update",
                    "offer_compensation"
                ],
                "llm_model": settings.AGENT_MODEL,
                "auth_method": "api_key",
                "specialization": "customer_communication",
                "tone_modes": ["formal", "professional", "apologetic", "reassuring", "urgent"],
                "languages": ["en"],
                "response_time_sla": "< 2 seconds"
            }
        ),
        
         # Skills
        skills=[
            AgentSkill(
                id="shipment_status_inquiry",
                name="Shipment Status Inquiry",
                description="Respond to customer inquiries about shipment status and current location",
                tags=["shipment", "status", "tracking", "inquiry"],
                examples=[
                    "What's the status of my shipment #ABC123?",
                    "Where is my package with ticket ID XYZ789?",
                    "Has my order #123456 been delivered yet?"
                ]
            ),
            AgentSkill(
                id="delay_explanation",
                name="Delay Explanation",
                description="Explain reasons for shipment delays with appropriate tone and context",
                tags=["delay", "explanation", "anomaly", "communication"],
                examples=[
                    "Why is my shipment delayed?",
                    "What happened to my package #ABC123?",
                    "Can you explain the delay with my order?"
                ]
            ),
            AgentSkill(
                id="eta_updates",
                name="ETA Updates",
                description="Provide updated estimated time of arrival for delayed shipments",
                tags=["eta", "delivery", "time", "update"],
                examples=[
                    "When will my package arrive now?",
                    "What's the new delivery date for #ABC123?",
                    "How long is the delay going to be?"
                ]
            ),
            AgentSkill(
                id="proactive_updates",
                name="Proactive Status Updates",
                description="Generate proactive customer notifications about shipment anomalies",
                tags=["proactive", "notification", "update", "anomaly"],
                examples=[
                    "Generate an update for a 2-hour traffic delay",
                    "Create a weather delay notification",
                    "Notify customer about vehicle breakdown"
                ]
            ),
            AgentSkill(
                id="compensation_handling",
                name="Compensation and Support",
                description="Handle compensation offers and support requests for major delays",
                tags=["compensation", "support", "customer_service", "delay"],
                examples=[
                    "What compensation can you offer for this delay?",
                    "I need help with my delayed shipment",
                    "This delay is unacceptable, what are you doing about it?"
                ]
            )
        ]
    )