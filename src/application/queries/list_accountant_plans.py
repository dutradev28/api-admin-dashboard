from pydantic import BaseModel
from decimal import Decimal
from typing import List
from sqlmodel import Session, select
from infrastructure.database.models import AccountantPlanModel

class AccountantPlanDTO(BaseModel):
    id: str
    name: str
    price: Decimal
    description: str | None

class ListAccountantPlansQuery(BaseModel):
    accountant_id: str

class ListAccountantPlansHandler:
    def __init__(self, session: Session):
        self.session = session

    def handle(self, query: ListAccountantPlansQuery) -> List[AccountantPlanDTO]:
        statement = select(AccountantPlanModel).where(
            AccountantPlanModel.accountant_id == query.accountant_id
        )
        plans = self.session.exec(statement).all()
        
        return [
            AccountantPlanDTO(
                id=plan.id,
                name=plan.name,
                price=plan.price,
                description=plan.description
            )
            for plan in plans
        ]
