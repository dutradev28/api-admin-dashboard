from datetime import datetime
from pydantic import BaseModel
from sqlmodel import Session, select
from src.infrastructure.database.models import SubscriptionModel

class AssignPlanCommand(BaseModel):
    accountant_id: str
    plan_id: str
    expires_at: datetime

class AssignPlanHandler:
    def __init__(self, session: Session):
        self.session = session

    def handle(self, command: AssignPlanCommand) -> SubscriptionModel:
        # Check if subscription already exists for this accountant
        statement = select(SubscriptionModel).where(SubscriptionModel.accountant_id == command.accountant_id)
        subscription = self.session.exec(statement).first()
        
        if subscription:
            # Update existing subscription
            subscription.plan_id = command.plan_id
            subscription.expires_at = command.expires_at
            subscription.status = "active"
        else:
            # Create new subscription
            subscription = SubscriptionModel(
                accountant_id=command.accountant_id,
                plan_id=command.plan_id,
                expires_at=command.expires_at,
                status="active"
            )
            self.session.add(subscription)
        
        self.session.commit()
        self.session.refresh(subscription)
        return subscription
