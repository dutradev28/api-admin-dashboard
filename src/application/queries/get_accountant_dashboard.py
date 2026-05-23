from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from sqlmodel import Session, select
from src.infrastructure.database.models import AccountantModel, SubscriptionModel, SystemPlanModel

class DashboardDTO(BaseModel):
    accountant_name: str
    primary_color: str
    secondary_color: str
    plan_name: Optional[str] = None
    expires_at: Optional[datetime] = None

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
            # Try to get just the accountant if the join failed due to some reason 
            # (though with outer join it should return something if accountant exists)
            accountant = self.session.get(AccountantModel, query.accountant_id)
            if not accountant:
                raise ValueError("Accountant not found")
            return DashboardDTO(
                accountant_name=accountant.name,
                primary_color=accountant.primary_color,
                secondary_color=accountant.secondary_color
            )

        accountant, subscription, plan = result
        return DashboardDTO(
            accountant_name=accountant.name,
            primary_color=accountant.primary_color,
            secondary_color=accountant.secondary_color,
            plan_name=plan.name if plan else None,
            expires_at=subscription.expires_at if subscription else None
        )
