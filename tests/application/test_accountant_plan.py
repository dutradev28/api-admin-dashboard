import pytest
from decimal import Decimal
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from infrastructure.database.models import AccountantPlanModel, AccountantModel
from application.commands.manage_accountant_plan import (
    CreateAccountantPlanCommand, 
    CreateAccountantPlanHandler,
    DeleteAccountantPlanCommand,
    DeleteAccountantPlanHandler
)

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

@pytest.fixture(name="accountant")
def accountant_fixture(session: Session):
    accountant = AccountantModel(name="Test Accountant", cnpj="12345678901234")
    session.add(accountant)
    session.commit()
    session.refresh(accountant)
    return accountant

def test_create_accountant_plan_command(session: Session, accountant: AccountantModel):
    # Given
    command = CreateAccountantPlanCommand(
        accountant_id=accountant.id,
        name="Basic Client Plan",
        price=Decimal("49.90"),
        description="A basic plan for clients"
    )
    handler = CreateAccountantPlanHandler(session)
    
    # When
    plan = handler.handle(command)
    
    # Then
    assert plan.id is not None
    assert plan.accountant_id == accountant.id
    assert plan.name == "Basic Client Plan"
    assert plan.price == Decimal("49.90")
    assert plan.description == "A basic plan for clients"
    
    # Verify in DB
    db_plan = session.get(AccountantPlanModel, plan.id)
    assert db_plan is not None
    assert db_plan.name == "Basic Client Plan"

def test_delete_accountant_plan_command(session: Session, accountant: AccountantModel):
    # Given
    plan = AccountantPlanModel(
        accountant_id=accountant.id,
        name="To be deleted",
        price=Decimal("10.00")
    )
    session.add(plan)
    session.commit()
    session.refresh(plan)
    
    command = DeleteAccountantPlanCommand(id=plan.id)
    handler = DeleteAccountantPlanHandler(session)
    
    # When
    handler.handle(command)
    
    # Then
    db_plan = session.get(AccountantPlanModel, plan.id)
    assert db_plan is None
