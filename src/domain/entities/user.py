from dataclasses import dataclass
from enum import Enum

class UserRole(str, Enum):
    SUPERADMIN = "superadmin"
    ACCOUNTANT = "accountant"
    CLIENT = "client"

@dataclass
class User:
    id: str
    email: str
    password_hash: str
    role: UserRole
    accountant_id: str | None = None
