from app.domain.entities.anomaly import Anomaly, AnomalyType, AnomalySeverity
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


# Mock anomaly database
MOCK_ANOMALIES = {
    "ABC123": {
        "anomaly_id": "ANO-001",
        "type": "traffic_jam",
        "timestamp": datetime.now() - timedelta(hours=2),
        "description": "Heavy traffic congestion on I-95 North due to multi-vehicle accident",
        "severity": "medium",
        "expected_delay_hours": 3.0,
        "new_route": "Rerouted via US-1 to avoid congestion",
        "support_needed": False,
        "resolution_notes": "Driver has taken alternate route, monitoring progress"
    },
    "DEF456": {
        "anomaly_id": "ANO-002", 
        "type": "weather",
        "timestamp": datetime.now() - timedelta(hours=1),
        "description": "Severe thunderstorm warning in delivery area",
        "severity": "high",
        "expected_delay_hours": 5.0,
        "new_route": None,
        "support_needed": False,
        "resolution_notes": "Delivery postponed until weather clears for safety"
    }
}


def get_anomaly_details(ticket_id: str) -> Optional[Dict[str, Any]]:
    """Get details about any anomalies affecting a shipment.
    
    Args:
        ticket_id: The shipment ticket ID to check for anomalies
        
    Returns:
        Dictionary containing anomaly details if found, None otherwise
    """
    try:
        ticket_id = ticket_id.upper()
        
        # In production, this would query a real database
        if ticket_id not in MOCK_ANOMALIES:
            return None
        
        anomaly_data = MOCK_ANOMALIES[ticket_id]
        
        # Create anomaly object
        anomaly = Anomaly(
            anomaly_id=anomaly_data["anomaly_id"],
            ticket_id=ticket_id,
            type=AnomalyType(anomaly_data["type"]),
            timestamp=anomaly_data["timestamp"],
            description=anomaly_data["description"],
            severity=AnomalySeverity(anomaly_data["severity"]),
            expected_delay_hours=anomaly_data["expected_delay_hours"],
            new_route=anomaly_data["new_route"],
            support_needed=anomaly_data["support_needed"],
            resolution_notes=anomaly_data["resolution_notes"]
        )
        
        # Calculate time since anomaly
        time_since = datetime.now() - anomaly.timestamp
        hours_since = time_since.total_seconds() / 3600
        
        return {
            "anomaly_id": anomaly.anomaly_id,
            "ticket_id": anomaly.ticket_id,
            "type": anomaly.type.value,
            "type_display": anomaly.type.value.replace("_", " ").title(),
            "timestamp": anomaly.timestamp.isoformat(),
            "hours_since_anomaly": round(hours_since, 1),
            "description": anomaly.description,
            "severity": anomaly.severity.value,
            "expected_delay_hours": anomaly.expected_delay_hours,
            "new_route": anomaly.new_route,
            "support_needed": anomaly.support_needed,
            "resolution_notes": anomaly.resolution_notes
        }
        
    except Exception as e:
        return {"error": f"Error processing anomaly data: {str(e)}"}
