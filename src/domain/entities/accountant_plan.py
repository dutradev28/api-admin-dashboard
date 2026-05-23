from dataclasses import dataclass
from decimal import Decimal

@dataclass
class AccountantPlan:
    id: str
    accountant_id: str
    name: str
    price: Decimal
    description: str | None = None
