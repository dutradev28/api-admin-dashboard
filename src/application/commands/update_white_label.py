from pydantic import BaseModel
from sqlmodel import Session
from infrastructure.database.models import AccountantModel

class UpdateWhiteLabelCommand(BaseModel):
    accountant_id: str
    logo_url: str
    primary_color: str
    secondary_color: str

class UpdateWhiteLabelHandler:
    def __init__(self, session: Session):
        self.session = session

    def handle(self, command: UpdateWhiteLabelCommand) -> AccountantModel:
        accountant = self.session.get(AccountantModel, command.accountant_id)
        if not accountant:
            raise ValueError(f"Accountant with id {command.accountant_id} not found")
        
        accountant.logo_url = command.logo_url
        accountant.primary_color = command.primary_color
        accountant.secondary_color = command.secondary_color
        
        self.session.add(accountant)
        self.session.commit()
        self.session.refresh(accountant)
        return accountant
