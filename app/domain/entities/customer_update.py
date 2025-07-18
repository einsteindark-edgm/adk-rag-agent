from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List


class UpdateTone(Enum):
    FORMAL = "formal"
    PROFESSIONAL = "professional"
    APOLOGETIC = "apologetic"
    REASSURING = "reassuring"
    URGENT = "urgent"


@dataclass
class CustomerUpdate:
    update_id: str
    ticket_id: str
    timestamp: datetime
    tone: UpdateTone
    subject: str
    message: str
    includes_new_eta: bool
    delay_duration_hours: Optional[float] = None
    compensation_offered: Optional[str] = None
    action_required: bool = False
    follow_up_needed: bool = False