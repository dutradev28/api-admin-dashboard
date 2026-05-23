from pydantic import EmailStr
from sqlmodel import Session, select
from infrastructure.database.models import UserModel
from infrastructure.security.password_recovery import create_recovery_token
from pydantic import BaseModel

class ForgotPasswordCommand(BaseModel):
    email: EmailStr

class ForgotPasswordHandler:
    def __init__(self, session: Session):
        self.session = session

    def handle(self, command: ForgotPasswordCommand) -> str:
        # 1. Verify if user exists
        user = self.session.exec(
            select(UserModel).where(UserModel.email == command.email)
        ).first()

        if not user:
            raise ValueError("User not found")

        # 2. Generate recovery token
        token = create_recovery_token(command.email)

        # 3. Return the token
        return token
