from pydantic import BaseModel
from decimal import Decimal
from sqlmodel import Session
from infrastructure.database.models import AccountantPlanModel

class CreateAccountantPlanCommand(BaseModel):
    accountant_id: str
    name: str
    price: Decimal
    description: str | None = None

class CreateAccountantPlanHandler:
    def __init__(self, session: Session):
        self.session = session

    def handle(self, command: CreateAccountantPlanCommand) -> AccountantPlanModel:
        plan = AccountantPlanModel(
            accountant_id=command.accountant_id,
            name=command.name,
            price=command.price,
            description=command.description
        )
        self.session.add(plan)
        self.session.commit()
        self.session.refresh(plan)
        return plan

class DeleteAccountantPlanCommand(BaseModel):
    id: str

class DeleteAccountantPlanHandler:
    def __init__(self, session: Session):
        self.session = session

    def handle(self, command: DeleteAccountantPlanCommand) -> None:
        plan = self.session.get(AccountantPlanModel, command.id)
        if plan:
            self.session.delete(plan)
            self.session.commit()
