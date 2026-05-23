from pydantic import BaseModel
from sqlmodel import Session, select
from infrastructure.database.models import AccountantModel, UserModel
from infrastructure.security.hashing import hash_password
from domain.entities.user import UserRole

class SignUpCommand(BaseModel):
    name: str
    cnpj: str
    email: str
    password: str

class SignUpHandler:
    def __init__(self, session: Session):
        self.session = session

    def handle(self, command: SignUpCommand) -> AccountantModel:
        # 1. Check if email already exists
        email_statement = select(UserModel).where(UserModel.email == command.email)
        existing_user = self.session.exec(email_statement).first()
        if existing_user:
            raise ValueError("Email already registered")

        # 2. Check if CNPJ already exists
        cnpj_statement = select(AccountantModel).where(AccountantModel.cnpj == command.cnpj)
        existing_acc = self.session.exec(cnpj_statement).first()
        if existing_acc:
            raise ValueError("CNPJ already registered")

        # 3. Hash password
        hashed_pw = hash_password(command.password)
        
        # 4. Create Accountant
        accountant = AccountantModel(
            name=command.name,
            cnpj=command.cnpj
        )
        self.session.add(accountant)
        self.session.flush() # To get the accountant.id
        
        # 5. Create User (Owner)
        user = UserModel(
            email=command.email,
            password_hash=hashed_pw,
            role=UserRole.ACCOUNTANT.value,
            accountant_id=accountant.id
        )
        self.session.add(user)
        
        # 6. Commit
        self.session.commit()
        self.session.refresh(accountant)
        return accountant
