from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

class SubscriptionStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    INACTIVE = "inactive"

@dataclass
class Subscription:
    id: str
    accountant_id: str
    plan_id: str
    status: SubscriptionStatus
    expires_at: datetime

    @property
    def is_valid(self) -> bool:
        return (
            self.status == SubscriptionStatus.ACTIVE and 
            self.expires_at > datetime.now(timezone.utc)
        )
