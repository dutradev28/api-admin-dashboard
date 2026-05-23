from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select
from infrastructure.database.models import UserModel
from infrastructure.security.hashing import verify_password
from infrastructure.security.tokens import create_access_token

class LoginQuery(BaseModel):
    email: EmailStr
    password: str

class LoginHandler:
    def __init__(self, session: Session):
        self.session = session

    def handle(self, query: LoginQuery) -> str:
        # 1. Find user
        statement = select(UserModel).where(UserModel.email == query.email)
        user = self.session.exec(statement).first()
        
        if not user:
            raise ValueError("Invalid email or password")
        
        # 2. Verify password
        if not verify_password(query.password, user.password_hash):
            raise ValueError("Invalid email or password")
        
        # 3. Create access token
        # We include email (as sub), role, and accountant_id in the payload
        token_data = {
            "sub": user.email,
            "role": user.role,
            "accountant_id": user.accountant_id
        }
        
        return create_access_token(token_data)
