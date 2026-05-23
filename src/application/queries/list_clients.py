from pydantic import BaseModel
from sqlmodel import Session, select
from infrastructure.database.models import ClientModel
from typing import List

class ListClientsQuery(BaseModel):
    accountant_id: str

class ListClientsHandler:
    def __init__(self, session: Session):
        self.session = session

    def handle(self, query: ListClientsQuery) -> List[ClientModel]:
        statement = select(ClientModel).where(
            ClientModel.accountant_id == query.accountant_id
        )
        results = self.session.exec(statement).all()
        return list(results)
