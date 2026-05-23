from pydantic import BaseModel
from sqlmodel import Session, select
from infrastructure.database.models import ClientModel

class CreateClientCommand(BaseModel):
    accountant_id: str
    name: str
    email: str
    cnpj: str

class CreateClientHandler:
    def __init__(self, session: Session):
        self.session = session

    def handle(self, command: CreateClientCommand) -> ClientModel:
        client = ClientModel(
            accountant_id=command.accountant_id,
            name=command.name,
            email=command.email,
            cnpj=command.cnpj
        )
        self.session.add(client)
        self.session.commit()
        self.session.refresh(client)
        return client

class UpdateClientCommand(BaseModel):
    id: str
    accountant_id: str
    name: str
    email: str

class UpdateClientHandler:
    def __init__(self, session: Session):
        self.session = session

    def handle(self, command: UpdateClientCommand) -> ClientModel:
        statement = select(ClientModel).where(
            ClientModel.id == command.id,
            ClientModel.accountant_id == command.accountant_id
        )
        client = self.session.exec(statement).first()
        
        if not client:
            raise ValueError("Client not found or does not belong to this accountant")
            
        client.name = command.name
        client.email = command.email
        
        self.session.add(client)
        self.session.commit()
        self.session.refresh(client)
        return client

class DeleteClientCommand(BaseModel):
    id: str
    accountant_id: str

class DeleteClientHandler:
    def __init__(self, session: Session):
        self.session = session

    def handle(self, command: DeleteClientCommand) -> None:
        statement = select(ClientModel).where(
            ClientModel.id == command.id,
            ClientModel.accountant_id == command.accountant_id
        )
        client = self.session.exec(statement).first()
        
        if not client:
            raise ValueError("Client not found or does not belong to this accountant")
            
        self.session.delete(client)
        self.session.commit()
