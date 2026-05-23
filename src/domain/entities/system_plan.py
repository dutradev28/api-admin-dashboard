from dataclasses import dataclass

@dataclass
class SystemPlan:
    id: str
    name: str
    description: str
    price: float
    max_clients: int
    is_active: bool = True
