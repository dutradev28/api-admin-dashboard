import pytest
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool
from application.commands.sign_up import SignUpCommand, SignUpHandler
from infrastructure.database.models import AccountantModel, UserModel
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

def test_sign_up_success(session: Session):
    # Given
    command = SignUpCommand(
        name="New Accountant Firm",
        cnpj="11222333000199",
        email="admin@firm.com",
        password="secure_password"
    )
    handler = SignUpHandler(session)
    
    # When
    accountant = handler.handle(command)
    
    # Then
    assert accountant.id is not None
    assert accountant.name == "New Accountant Firm"
    
    # Verify User was created with ACCOUNTANT role
    user = session.exec(select(UserModel).where(UserModel.email == "admin@firm.com")).first()
    assert user is not None
    assert user.accountant_id == accountant.id
    assert user.role == UserRole.ACCOUNTANT.value
    assert user.password_hash != "secure_password"

def test_sign_up_fails_if_email_exists(session: Session):
    # Given: an existing user
    existing_user = UserModel(
        email="existing@test.com",
        password_hash="hashed",
        role=UserRole.ACCOUNTANT.value
    )
    session.add(existing_user)
    session.commit()
    
    command = SignUpCommand(
        name="Another Firm",
        cnpj="44555666000100",
        email="existing@test.com",
        password="password"
    )
    handler = SignUpHandler(session)
    
    # When / Then
    with pytest.raises(ValueError) as excinfo:
        handler.handle(command)
    assert "Email already registered" in str(excinfo.value)

def test_sign_up_fails_if_cnpj_exists(session: Session):
    # Given: an existing accountant
    existing_acc = AccountantModel(
        name="Existing Firm",
        cnpj="77888999000111"
    )
    session.add(existing_acc)
    session.commit()
    
    command = SignUpCommand(
        name="Attempted Firm",
        cnpj="77888999000111",
        email="new@test.com",
        password="password"
    )
    handler = SignUpHandler(session)
    
    # When / Then
    with pytest.raises(ValueError) as excinfo:
        handler.handle(command)
    assert "CNPJ already registered" in str(excinfo.value)
