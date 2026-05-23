import pytest
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool
from application.commands.create_accountant import CreateAccountantCommand, CreateAccountantHandler
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

def test_create_accountant_command(session: Session):
    # Given
    command = CreateAccountantCommand(
        name="Test Accountant",
        cnpj="12345678000199",
        email="owner@test.com",
        password="securepassword"
    )
    handler = CreateAccountantHandler(session)
    
    # When
    accountant = handler.handle(command)
    
    # Then
    assert accountant.id is not None
    assert accountant.name == "Test Accountant"
    assert accountant.cnpj == "12345678000199"
    
    # Verify User was created
    user = session.exec(select(UserModel).where(UserModel.email == "owner@test.com")).first()
    assert user is not None
    assert user.accountant_id == accountant.id
    assert user.role == UserRole.ACCOUNTANT.value
    
    # Verify password was hashed
    assert user.password_hash != "securepassword"
