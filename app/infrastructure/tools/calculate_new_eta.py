from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import random


# Mock traffic and weather data
MOCK_TRAFFIC_CONDITIONS = {
    "clear": 1.0,      # No delay multiplier
    "light": 1.1,      # 10% slower
    "moderate": 1.3,   # 30% slower
    "heavy": 1.8,      # 80% slower
    "severe": 2.5      # 150% slower
}

MOCK_WEATHER_CONDITIONS = {
    "clear": 1.0,
    "rain": 1.2,
    "heavy_rain": 1.5,
    "storm": 2.0,
    "snow": 2.5
}


def calculate_new_eta(
    ticket_id: str,
    original_eta: str,
    anomaly_type: str,
    severity: str
) -> Dict[str, Any]:
    """Calculate a new ETA based on anomaly type and current conditions.
    
    Args:
        ticket_id: The shipment ticket ID
        original_eta: Original ETA in ISO format
        anomaly_type: Type of anomaly (traffic_jam, weather, etc.)
        severity: Severity level (low, medium, high, critical)
        
    Returns:
        Dictionary containing new ETA calculation details
    """
    # Parse original ETA
    original_dt = datetime.fromisoformat(original_eta)
    
    # Base delay based on severity
    severity_delays = {
        "low": 0.5,      # 30 minutes
        "medium": 2.0,    # 2 hours
        "high": 4.0,      # 4 hours
        "critical": 8.0   # 8 hours
    }
    
    base_delay_hours = severity_delays.get(severity, 2.0)
    
    # Additional factors based on anomaly type
    anomaly_multipliers = {
        "traffic_jam": 1.2,
        "weather": 1.5,
        "vehicle_breakdown": 2.0,
        "accident": 1.8,
        "route_deviation": 1.1,
        "driver_issue": 1.3,
        "customs_delay": 2.5,
        "other": 1.0
    }
    
    multiplier = anomaly_multipliers.get(anomaly_type, 1.0)
    
    # Mock API calls for current conditions
    # In production, these would be real API calls
    current_traffic = random.choice(list(MOCK_TRAFFIC_CONDITIONS.keys()))
    current_weather = random.choice(list(MOCK_WEATHER_CONDITIONS.keys()))
    
    traffic_factor = MOCK_TRAFFIC_CONDITIONS[current_traffic]
    weather_factor = MOCK_WEATHER_CONDITIONS[current_weather]
    
    # Calculate total delay
    total_delay_hours = base_delay_hours * multiplier * traffic_factor * weather_factor
    
    # Add some randomness for realism (±15%)
    variance = random.uniform(0.85, 1.15)
    total_delay_hours *= variance
    
    # Calculate new ETA
    new_eta = original_dt + timedelta(hours=total_delay_hours)
    
    # Ensure new ETA is in the future
    if new_eta <= datetime.now():
        new_eta = datetime.now() + timedelta(hours=1)
        total_delay_hours = (new_eta - original_dt).total_seconds() / 3600
    
    # Calculate confidence based on data quality
    confidence = 0.85  # Base confidence
    if severity == "critical":
        confidence *= 0.8
    if anomaly_type in ["weather", "vehicle_breakdown"]:
        confidence *= 0.9
        
    return {
        "ticket_id": ticket_id,
        "original_eta": original_eta,
        "new_eta": new_eta.isoformat(),
        "total_delay_hours": round(total_delay_hours, 1),
        "delay_breakdown": {
            "base_delay": base_delay_hours,
            "anomaly_factor": multiplier,
            "traffic_factor": traffic_factor,
            "weather_factor": weather_factor
        },
        "current_conditions": {
            "traffic": current_traffic,
            "weather": current_weather
        },
        "confidence_level": round(confidence, 2),
        "last_updated": datetime.now().isoformat()
    }
