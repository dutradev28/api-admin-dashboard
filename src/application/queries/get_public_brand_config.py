from pydantic import BaseModel
from typing import Optional
from sqlmodel import Session
from src.infrastructure.database.models import AccountantModel

class PublicBrandDTO(BaseModel):
    primary_color: str
    secondary_color: str
    logo_url: Optional[str]

class GetPublicBrandConfigQuery(BaseModel):
    accountant_id: str

class GetPublicBrandConfigHandler:
    def __init__(self, session: Session):
        self.session = session

    def handle(self, query: GetPublicBrandConfigQuery) -> PublicBrandDTO:
        accountant = self.session.get(AccountantModel, query.accountant_id)
        if not accountant:
            raise ValueError("Accountant not found")
        
        return PublicBrandDTO(
            primary_color=accountant.primary_color,
            secondary_color=accountant.secondary_color,
            logo_url=accountant.logo_url
        )
