from app.domain.entities.customer_update import UpdateTone
from datetime import datetime
from typing import Dict, Any, Optional
import uuid


MESSAGE_TEMPLATES = {
    "initial_delay": {
        UpdateTone.PROFESSIONAL: """Dear {customer_name},

We are writing to inform you about a delay affecting your shipment #{ticket_id}.

Reason: {reason}
Original delivery time: {original_eta}
New estimated delivery time: {new_eta}
Delay duration: {delay_hours} hours

We are actively monitoring your shipment and will provide updates as the situation develops.

Best regards,
Logistics Team""",
        
        UpdateTone.APOLOGETIC: """Dear {customer_name},

We sincerely apologize for the inconvenience, but your shipment #{ticket_id} has encountered a delay.

What happened: {reason}
Original delivery: {original_eta}
New delivery estimate: {new_eta}
Total delay: {delay_hours} hours

We understand this disruption may affect your plans, and we're working diligently to minimize the delay. {compensation_text}

With our sincere apologies,
Logistics Team""",
        
        UpdateTone.URGENT: """URGENT: Shipment #{ticket_id} Delay Notice

{customer_name}, immediate attention required.

Critical delay detected: {reason}
Expected delay: {delay_hours} hours
New ETA: {new_eta}

Action may be required on your end. Our team is standing by to assist.

Contact us immediately if this delay critically impacts your operations."""
    },
    
    "status_update": {
        UpdateTone.PROFESSIONAL: """Dear {customer_name},

Status update for shipment #{ticket_id}:

Current status: {status}
Location: En route from {origin} to {destination}
Expected arrival: {eta}

{additional_info}

Thank you for your patience.""",
        
        UpdateTone.REASSURING: """Hello {customer_name},

Good news about your shipment #{ticket_id}!

Despite the earlier {reason}, your package is making good progress:
- Current status: {status}
- Expected delivery: {eta}

Everything is under control, and we're confident your shipment will arrive as scheduled. We'll notify you of any changes.

Best regards,
Your Logistics Team"""
    }
}


def generate_customer_message(
    ticket_id: str,
    customer_name: str,
    message_type: str,
    tone: str,
    reason: str,
    original_eta: Optional[str] = None,
    new_eta: Optional[str] = None,
    delay_hours: Optional[float] = None,
    offer_compensation: bool = False,
    additional_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generate a customer communication message with appropriate tone.
    
    Args:
        ticket_id: Shipment ticket ID
        customer_name: Customer's name
        message_type: Type of message (initial_delay, status_update, etc.)
        tone: Desired tone (professional, apologetic, urgent, reassuring, formal)
        reason: Reason for the update/delay
        original_eta: Original ETA if applicable
        new_eta: New ETA if applicable
        delay_hours: Hours of delay if applicable
        offer_compensation: Whether to include compensation offer
        additional_context: Any additional context for the message
        
    Returns:
        Dictionary containing the generated message and metadata
    """
    # Convert tone string to enum
    tone_enum = UpdateTone(tone.lower())
    
    # Get appropriate template
    templates = MESSAGE_TEMPLATES.get(message_type, MESSAGE_TEMPLATES["status_update"])
    template = templates.get(tone_enum, templates[UpdateTone.PROFESSIONAL])
    
    # Prepare compensation text if needed
    compensation_text = ""
    if offer_compensation and delay_hours and delay_hours > 4:
        compensation_text = "\n\nAs an apology for this significant delay, we'd like to offer you a 15% discount on your next shipment."
    
    # Format dates for readability
    if original_eta:
        original_dt = datetime.fromisoformat(original_eta)
        original_eta_formatted = original_dt.strftime("%B %d, %Y at %I:%M %p")
    else:
        original_eta_formatted = "Not specified"
        
    if new_eta:
        new_dt = datetime.fromisoformat(new_eta)
        new_eta_formatted = new_dt.strftime("%B %d, %Y at %I:%M %p")
    else:
        new_eta_formatted = "To be determined"
    
    # Prepare context
    context_data = {
        "customer_name": customer_name,
        "ticket_id": ticket_id,
        "reason": reason,
        "original_eta": original_eta_formatted,
        "new_eta": new_eta_formatted,
        "eta": new_eta_formatted,
        "delay_hours": round(delay_hours, 1) if delay_hours else 0,
        "compensation_text": compensation_text,
        "status": "In Transit - Delayed" if delay_hours else "In Transit",
        "origin": additional_context.get("origin", "Origin") if additional_context else "Origin",
        "destination": additional_context.get("destination", "Destination") if additional_context else "Destination",
        "additional_info": additional_context.get("notes", "") if additional_context else ""
    }
    
    # Generate message
    message = template.format(**context_data)
    
    # Generate metadata
    update_id = f"UPD-{uuid.uuid4().hex[:8].upper()}"
    
    return {
        "update_id": update_id,
        "ticket_id": ticket_id,
        "timestamp": datetime.now().isoformat(),
        "message_type": message_type,
        "tone": tone,
        "subject": f"Shipment #{ticket_id} - {message_type.replace('_', ' ').title()}",
        "message": message.strip(),
        "includes_compensation": offer_compensation,
        "delay_severity": "high" if delay_hours and delay_hours > 4 else "medium" if delay_hours and delay_hours > 2 else "low",
        "follow_up_needed": delay_hours and delay_hours > 6 if delay_hours else False,
        "metadata": {
            "original_eta": original_eta,
            "new_eta": new_eta,
            "delay_hours": delay_hours,
            "reason": reason
        }
    }
