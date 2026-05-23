from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from sqlmodel import Session, select
from src.infrastructure.database.models import AccountantModel, SubscriptionModel, SystemPlanModel

class BrandDTO(BaseModel):
    primary_color: str
    secondary_color: str
    logo_url: Optional[str]

class SubscriptionDTO(BaseModel):
    plan_name: str
    status: str
    expires_at: datetime

class DashboardDTO(BaseModel):
    name: str
    cnpj: str
    brand: BrandDTO
    subscription: Optional[SubscriptionDTO]

class GetAccountantDashboardQuery(BaseModel):
    accountant_id: str

class GetAccountantDashboardHandler:
    def __init__(self, session: Session):
        self.session = session

    def handle(self, query: GetAccountantDashboardQuery) -> DashboardDTO:
        statement = (
            select(AccountantModel, SubscriptionModel, SystemPlanModel)
            .join(SubscriptionModel, AccountantModel.id == SubscriptionModel.accountant_id, isouter=True)
            .join(SystemPlanModel, SubscriptionModel.plan_id == SystemPlanModel.id, isouter=True)
            .where(AccountantModel.id == query.accountant_id)
            .where((SubscriptionModel.status == "active") | (SubscriptionModel.status == None))
        )
        
        result = self.session.exec(statement).first()
        
        if not result:
            accountant = self.session.get(AccountantModel, query.accountant_id)
            if not accountant:
                raise ValueError("Accountant not found")
            
            return DashboardDTO(
                name=accountant.name,
                cnpj=accountant.cnpj,
                brand=BrandDTO(
                    primary_color=accountant.primary_color,
                    secondary_color=accountant.secondary_color,
                    logo_url=accountant.logo_url
                ),
                subscription=None
            )

        accountant, subscription, plan = result
        
        subscription_dto = None
        if subscription and plan:
            subscription_dto = SubscriptionDTO(
                plan_name=plan.name,
                status=subscription.status,
                expires_at=subscription.expires_at
            )

        return DashboardDTO(
            name=accountant.name,
            cnpj=accountant.cnpj,
            brand=BrandDTO(
                primary_color=accountant.primary_color,
                secondary_color=accountant.secondary_color,
                logo_url=accountant.logo_url
            ),
            subscription=subscription_dto
        )
