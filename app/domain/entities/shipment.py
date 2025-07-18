from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class ShipmentStatus(Enum):
    IN_TRANSIT = "in_transit"
    DELAYED = "delayed"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


@dataclass
class Shipment:
    ticket_id: str
    origin: str
    destination: str
    customer_name: str
    customer_email: str
    original_eta: datetime
    current_eta: Optional[datetime] = None
    status: ShipmentStatus = ShipmentStatus.IN_TRANSIT
    priority: str = "standard"  # standard, express, priority
    value: Optional[float] = None
    description: Optional[str] = None