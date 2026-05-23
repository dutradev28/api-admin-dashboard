from dataclasses import dataclass
from sqlmodel import Session, select
from infrastructure.database.models import UserModel
from infrastructure.security.hashing import hash_password
from infrastructure.security.password_recovery import verify_recovery_token

@dataclass
class ResetPasswordCommand:
    token: str
    new_password: str

class ResetPasswordHandler:
    def __init__(self, session: Session):
        self.session = session

    def handle(self, command: ResetPasswordCommand):
        email = verify_recovery_token(command.token)
        if not email:
            raise ValueError("Invalid or expired recovery token")
        
        statement = select(UserModel).where(UserModel.email == email)
        user = self.session.exec(statement).first()
        
        if not user:
            raise ValueError("User not found")
        
        user.password_hash = hash_password(command.new_password)
        self.session.add(user)
        self.session.commit()
