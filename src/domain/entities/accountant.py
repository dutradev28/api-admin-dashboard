from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Accountant:
    id: str
    name: str
    cnpj: str
    logo_url: Optional[str] = None
    primary_color: str = "#000000"
    secondary_color: str = "#ffffff"
