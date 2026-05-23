import pytest
from decimal import Decimal
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from infrastructure.database.models import AccountantPlanModel, AccountantModel
from application.commands.manage_accountant_plan import (
    CreateAccountantPlanCommand, 
    CreateAccountantPlanHandler,
    UpdateAccountantPlanCommand,
    UpdateAccountantPlanHandler,
    DeleteAccountantPlanCommand,
    DeleteAccountantPlanHandler
)
from application.queries.list_accountant_plans import (
    ListAccountantPlansQuery,
    ListAccountantPlansHandler
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

@pytest.fixture(name="another_accountant")
def another_accountant_fixture(session: Session):
    accountant = AccountantModel(name="Another Accountant", cnpj="98765432109876")
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

def test_update_accountant_plan_command(session: Session, accountant: AccountantModel):
    # Given
    plan = AccountantPlanModel(
        accountant_id=accountant.id,
        name="Old Name",
        price=Decimal("10.00"),
        description="Old Description"
    )
    session.add(plan)
    session.commit()
    session.refresh(plan)
    
    command = UpdateAccountantPlanCommand(
        id=plan.id,
        accountant_id=accountant.id,
        name="New Name",
        price=Decimal("20.00"),
        description="New Description"
    )
    handler = UpdateAccountantPlanHandler(session)
    
    # When
    updated_plan = handler.handle(command)
    
    # Then
    assert updated_plan.name == "New Name"
    assert updated_plan.price == Decimal("20.00")
    assert updated_plan.description == "New Description"
    
    # Verify in DB
    db_plan = session.get(AccountantPlanModel, plan.id)
    assert db_plan.name == "New Name"

def test_update_accountant_plan_fails_for_other_accountant(session: Session, accountant: AccountantModel, another_accountant: AccountantModel):
    # Given
    plan = AccountantPlanModel(
        accountant_id=accountant.id,
        name="Accountant 1 Plan",
        price=Decimal("10.00")
    )
    session.add(plan)
    session.commit()
    session.refresh(plan)
    
    command = UpdateAccountantPlanCommand(
        id=plan.id,
        accountant_id=another_accountant.id,
        name="Trying to update",
        price=Decimal("20.00")
    )
    handler = UpdateAccountantPlanHandler(session)
    
    # When / Then
    with pytest.raises(ValueError, match="Plan not found or does not belong to this accountant"):
        handler.handle(command)

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
    
    command = DeleteAccountantPlanCommand(id=plan.id, accountant_id=accountant.id)
    handler = DeleteAccountantPlanHandler(session)
    
    # When
    handler.handle(command)
    
    # Then
    db_plan = session.get(AccountantPlanModel, plan.id)
    assert db_plan is None

def test_delete_accountant_plan_fails_for_other_accountant(session: Session, accountant: AccountantModel, another_accountant: AccountantModel):
    # Given
    plan = AccountantPlanModel(
        accountant_id=accountant.id,
        name="Accountant 1 Plan",
        price=Decimal("10.00")
    )
    session.add(plan)
    session.commit()
    session.refresh(plan)
    
    command = DeleteAccountantPlanCommand(id=plan.id, accountant_id=another_accountant.id)
    handler = DeleteAccountantPlanHandler(session)
    
    # When / Then
    with pytest.raises(ValueError, match="Plan not found or does not belong to this accountant"):
        handler.handle(command)
    
    # Verify still in DB
    db_plan = session.get(AccountantPlanModel, plan.id)
    assert db_plan is not None

def test_list_accountant_plans(session: Session, accountant: AccountantModel, another_accountant: AccountantModel):
    # Given
    plan1 = AccountantPlanModel(accountant_id=accountant.id, name="Plan 1", price=Decimal("10.00"))
    plan2 = AccountantPlanModel(accountant_id=accountant.id, name="Plan 2", price=Decimal("20.00"))
    other_plan = AccountantPlanModel(accountant_id=another_accountant.id, name="Other", price=Decimal("30.00"))
    
    session.add(plan1)
    session.add(plan2)
    session.add(other_plan)
    session.commit()
    
    query = ListAccountantPlansQuery(accountant_id=accountant.id)
    handler = ListAccountantPlansHandler(session)
    
    # When
    plans = handler.handle(query)
    
    # Then
    assert len(plans) == 2
    assert any(p.name == "Plan 1" for p in plans)
    assert any(p.name == "Plan 2" for p in plans)
    assert not any(p.name == "Other" for p in plans)
