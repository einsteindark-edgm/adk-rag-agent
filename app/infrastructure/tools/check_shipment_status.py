from app.domain.entities.shipment import Shipment, ShipmentStatus
from datetime import datetime, timedelta
import re
from typing import Dict, Any


# Mock database for testing
MOCK_SHIPMENTS = {
    "ABC123": {
        "origin": "Miami, FL",
        "destination": "New York, NY",
        "customer_name": "John Doe", 
        "customer_email": "john.doe@example.com",
        "original_eta": datetime.now() + timedelta(days=2),
        "current_eta": datetime.now() + timedelta(days=2, hours=3),
        "status": "delayed",
        "priority": "express",
        "value": 1250.00,
        "description": "Electronic equipment"
    },
    "XYZ789": {
        "origin": "Los Angeles, CA",
        "destination": "Chicago, IL",
        "customer_name": "Jane Smith",
        "customer_email": "jane.smith@example.com", 
        "original_eta": datetime.now() + timedelta(days=3),
        "current_eta": datetime.now() + timedelta(days=3),
        "status": "in_transit",
        "priority": "standard",
        "value": 450.00,
        "description": "Clothing items"
    }
}


def check_shipment_status(ticket_id: str) -> Dict[str, Any]:
    """Check the current status of a shipment by ticket ID.
    
    Args:
        ticket_id: The shipment ticket ID to look up
        
    Returns:
        Dictionary containing shipment details and current status
    """
    # Validate ticket ID format
    if not re.match(r"^[A-Z]{3}\d{3}$", ticket_id.upper()):
        return {"error": f"Invalid ticket ID format: {ticket_id}. Expected format: ABC123"}
    
    ticket_id = ticket_id.upper()
    
    # In production, this would query a real database
    if ticket_id not in MOCK_SHIPMENTS:
        return {"error": f"Shipment not found: {ticket_id}"}
    
    shipment_data = MOCK_SHIPMENTS[ticket_id]
    
    # Create shipment object
    shipment = Shipment(
        ticket_id=ticket_id,
        origin=shipment_data["origin"],
        destination=shipment_data["destination"],
        customer_name=shipment_data["customer_name"],
        customer_email=shipment_data["customer_email"],
        original_eta=shipment_data["original_eta"],
        current_eta=shipment_data["current_eta"],
        status=ShipmentStatus(shipment_data["status"]),
        priority=shipment_data["priority"],
        value=shipment_data["value"],
        description=shipment_data["description"]
    )
    
    # Calculate delay if any
    delay_hours = None
    if shipment.current_eta and shipment.original_eta:
        delay = shipment.current_eta - shipment.original_eta
        delay_hours = delay.total_seconds() / 3600
    
    return {
        "ticket_id": shipment.ticket_id,
        "status": shipment.status.value,
        "origin": shipment.origin,
        "destination": shipment.destination,
        "customer_name": shipment.customer_name,
        "original_eta": shipment.original_eta.isoformat(),
        "current_eta": shipment.current_eta.isoformat() if shipment.current_eta else None,
        "delay_hours": delay_hours,
        "priority": shipment.priority,
        "description": shipment.description
    }
