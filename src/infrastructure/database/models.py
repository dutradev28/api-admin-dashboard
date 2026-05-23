from sqlmodel import SQLModel, Field, Relationship, Column, Numeric
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
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
    subscriptions: List["SubscriptionModel"] = Relationship(back_populates="accountant")

class UserModel(SQLModel, table=True):
    __tablename__ = "users"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    role: str
    accountant_id: Optional[str] = Field(default=None, foreign_key="accountants.id")
    
    accountant: Optional[AccountantModel] = Relationship(back_populates="users")

class SystemPlanModel(SQLModel, table=True):
    __tablename__ = "system_plans"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    description: str
    price: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    max_clients: int
    is_active: bool = True

class SubscriptionModel(SQLModel, table=True):
    __tablename__ = "subscriptions"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    accountant_id: str = Field(foreign_key="accountants.id")
    plan_id: str = Field(foreign_key="system_plans.id")
    status: str = "active" # Will be mapped to Enum in app layer
    expires_at: datetime
    
    accountant: AccountantModel = Relationship(back_populates="subscriptions")
    plan: SystemPlanModel = Relationship()

class AccountantPlanModel(SQLModel, table=True):
    __tablename__ = "accountant_plans"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    accountant_id: str = Field(foreign_key="accountants.id")
    name: str
    price: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    description: Optional[str] = None
    
    accountant: "AccountantModel" = Relationship()

class ClientModel(SQLModel, table=True):
    __tablename__ = "clients"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    accountant_id: str = Field(foreign_key="accountants.id")
    accountant_plan_id: Optional[str] = Field(default=None, foreign_key="accountant_plans.id")
    name: str
    email: str = Field(index=True)
    cnpj: str = Field(index=True)
    status: str = "active"
    
    accountant: "AccountantModel" = Relationship()
    plan: Optional[AccountantPlanModel] = Relationship()
