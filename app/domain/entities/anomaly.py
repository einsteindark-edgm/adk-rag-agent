from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class AnomalyType(Enum):
    TRAFFIC_JAM = "traffic_jam"
    WEATHER = "weather"
    VEHICLE_BREAKDOWN = "vehicle_breakdown"
    ACCIDENT = "accident"
    ROUTE_DEVIATION = "route_deviation"
    DRIVER_ISSUE = "driver_issue"
    CUSTOMS_DELAY = "customs_delay"
    OTHER = "other"


class AnomalySeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Anomaly:
    anomaly_id: str
    ticket_id: str
    type: AnomalyType
    timestamp: datetime
    description: str
    severity: AnomalySeverity
    expected_delay_hours: Optional[float] = None
    new_route: Optional[str] = None
    support_needed: bool = False
    resolution_notes: Optional[str] = None