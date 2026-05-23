from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
import uuid

class AccountantModel(SQLModel, table=True):
    __tablename__ = "accountants"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    cnpj: str = Field(index=True, unique=True)
    logo_url: Optional[str] = None
    primary_color: str = "#000000"
    secondary_color: str = "#ffffff"
    
    users: List["UserModel"] = Relationship(back_populates="accountant")

class UserModel(SQLModel, table=True):
    __tablename__ = "users"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    role: str
    accountant_id: Optional[str] = Field(default=None, foreign_key="accountants.id")
    
    accountant: Optional[AccountantModel] = Relationship(back_populates="users")
