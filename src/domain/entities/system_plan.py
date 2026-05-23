from dataclasses import dataclass
from decimal import Decimal

@dataclass
class SystemPlan:
    id: str
    name: str
    description: str
    price: Decimal
    max_clients: int
    is_active: bool = True
