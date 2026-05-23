import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from application.commands.update_white_label import UpdateWhiteLabelCommand, UpdateWhiteLabelHandler
from infrastructure.database.models import AccountantModel

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

def test_update_white_label_command(session: Session):
    # Given
    accountant = AccountantModel(
        name="Test Accountant",
        cnpj="12345678000199",
        logo_url="http://old.logo",
        primary_color="#000000",
        secondary_color="#ffffff"
    )
    session.add(accountant)
    session.commit()
    session.refresh(accountant)

    command = UpdateWhiteLabelCommand(
        accountant_id=accountant.id,
        logo_url="http://new.logo",
        primary_color="#FF0000",
        secondary_color="#00FF00"
    )
    handler = UpdateWhiteLabelHandler(session)
    
    # When
    updated_accountant = handler.handle(command)
    
    # Then
    assert updated_accountant.logo_url == "http://new.logo"
    assert updated_accountant.primary_color == "#FF0000"
    assert updated_accountant.secondary_color == "#00FF00"

    # Verify in DB
    session.refresh(accountant)
    assert accountant.logo_url == "http://new.logo"
    assert accountant.primary_color == "#FF0000"
    assert accountant.secondary_color == "#00FF00"
