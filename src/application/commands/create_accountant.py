from pydantic import BaseModel
from sqlmodel import Session
from src.infrastructure.database.models import AccountantModel, UserModel
from src.infrastructure.security.hashing import hash_password
from src.domain.entities.user import UserRole

class CreateAccountantCommand(BaseModel):
    name: str
    cnpj: str
    email: str
    password: str

class CreateAccountantHandler:
    def __init__(self, session: Session):
        self.session = session

    def handle(self, command: CreateAccountantCommand) -> AccountantModel:
        # 1. Hash password
        hashed_pw = hash_password(command.password)
        
        # 2. Create Accountant
        accountant = AccountantModel(
            name=command.name,
            cnpj=command.cnpj
        )
        self.session.add(accountant)
        self.session.flush() # To get the accountant.id
        
        # 3. Create User
        user = UserModel(
            email=command.email,
            password_hash=hashed_pw,
            role=UserRole.ACCOUNTANT.value,
            accountant_id=accountant.id
        )
        self.session.add(user)
        
        # 4. Commit
        self.session.commit()
        self.session.refresh(accountant)
        return accountant
