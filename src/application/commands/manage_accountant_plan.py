from pydantic import BaseModel
from decimal import Decimal
from sqlmodel import Session, select
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

class UpdateAccountantPlanCommand(BaseModel):
    id: str
    accountant_id: str
    name: str
    price: Decimal
    description: str | None = None

class UpdateAccountantPlanHandler:
    def __init__(self, session: Session):
        self.session = session

    def handle(self, command: UpdateAccountantPlanCommand) -> AccountantPlanModel:
        statement = select(AccountantPlanModel).where(
            AccountantPlanModel.id == command.id,
            AccountantPlanModel.accountant_id == command.accountant_id
        )
        plan = self.session.exec(statement).first()
        
        if not plan:
            raise ValueError("Plan not found or does not belong to this accountant")
            
        plan.name = command.name
        plan.price = command.price
        plan.description = command.description
        
        self.session.add(plan)
        self.session.commit()
        self.session.refresh(plan)
        return plan

class DeleteAccountantPlanCommand(BaseModel):
    id: str
    accountant_id: str

class DeleteAccountantPlanHandler:
    def __init__(self, session: Session):
        self.session = session

    def handle(self, command: DeleteAccountantPlanCommand) -> None:
        statement = select(AccountantPlanModel).where(
            AccountantPlanModel.id == command.id,
            AccountantPlanModel.accountant_id == command.accountant_id
        )
        plan = self.session.exec(statement).first()
        
        if plan:
            self.session.delete(plan)
            self.session.commit()
        else:
            # If it doesn't exist or doesn't belong to the accountant, we might want to raise an error
            # but for idempotency, sometimes we just ignore. 
            # Given the request to "verify that the plan belongs to that accountant before deleting", 
            # I'll raise an error if not found to be strict.
            raise ValueError("Plan not found or does not belong to this accountant")
