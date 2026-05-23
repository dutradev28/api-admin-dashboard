from dataclasses import dataclass

@dataclass
class Client:
    id: str
    accountant_id: str
    name: str
    email: str
    cnpj: str
    accountant_plan_id: str | None = None
    status: str = "active"
