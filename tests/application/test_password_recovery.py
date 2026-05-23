import pytest
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool
from infrastructure.database.models import UserModel
from infrastructure.security.hashing import hash_password, verify_password
from infrastructure.security.password_recovery import create_recovery_token
from application.commands.reset_password import ResetPasswordCommand, ResetPasswordHandler
from domain.entities.user import UserRole

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_reset_password_success(session: Session):
    # Given
    email = "user@example.com"
    old_password = "oldpassword123"
    new_password = "newpassword456"
    user = UserModel(
        email=email,
        password_hash=hash_password(old_password),
        role=UserRole.CLIENT.value
    )
    session.add(user)
    session.commit()

    token = create_recovery_token(email)
    command = ResetPasswordCommand(token=token, new_password=new_password)
    handler = ResetPasswordHandler(session)

    # When
    handler.handle(command)

    # Then
    session.expire_all()
    updated_user = session.exec(select(UserModel).where(UserModel.email == email)).first()
    assert verify_password(new_password, updated_user.password_hash)
    assert not verify_password(old_password, updated_user.password_hash)

def test_reset_password_invalid_token(session: Session):
    # Given
    invalid_token = "invalid.token.here"
    command = ResetPasswordCommand(token=invalid_token, new_password="newpassword123")
    handler = ResetPasswordHandler(session)

    # When / Then
    with pytest.raises(ValueError, match="Invalid or expired recovery token"):
        handler.handle(command)

def test_reset_password_user_not_found(session: Session):
    # Given
    email = "nonexistent@example.com"
    token = create_recovery_token(email)
    command = ResetPasswordCommand(token=token, new_password="newpassword123")
    handler = ResetPasswordHandler(session)

    # When / Then
    with pytest.raises(ValueError, match="User not found"):
        handler.handle(command)
