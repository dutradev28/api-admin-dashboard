from dataclasses import dataclass
from datetime import datetime

@dataclass
class Subscription:
    id: str
    accountant_id: str
    plan_id: str
    status: str  # "active", "expired", "inactive"
    expires_at: datetime
