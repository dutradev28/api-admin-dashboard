from pydantic import BaseModel
from decimal import Decimal
from sqlmodel import Session
from infrastructure.database.models import SystemPlanModel

class CreateSystemPlanCommand(BaseModel):
    name: str
    description: str
    price: Decimal
    max_clients: int
    is_active: bool = True

class CreateSystemPlanHandler:
    def __init__(self, session: Session):
        self.session = session

    def handle(self, command: CreateSystemPlanCommand) -> SystemPlanModel:
        plan = SystemPlanModel(
            name=command.name,
            description=command.description,
            price=command.price,
            max_clients=command.max_clients,
            is_active=command.is_active
        )
        self.session.add(plan)
        self.session.commit()
        self.session.refresh(plan)
        return plan
