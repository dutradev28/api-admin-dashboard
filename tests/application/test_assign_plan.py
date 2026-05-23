import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool
from src.application.commands.assign_plan import AssignPlanCommand, AssignPlanHandler
from src.infrastructure.database.models import AccountantModel, SystemPlanModel, SubscriptionModel

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

def test_assign_plan_command(session: Session):
    # Given: An accountant and a system plan
    accountant = AccountantModel(name="Test Accountant", cnpj="12345678000199")
    plan = SystemPlanModel(name="Basic Plan", description="Basic", price=100.0, max_clients=10)
    session.add(accountant)
    session.add(plan)
    session.commit()
    session.refresh(accountant)
    session.refresh(plan)

    expires_at = datetime.now() + timedelta(days=30)
    command = AssignPlanCommand(
        accountant_id=accountant.id,
        plan_id=plan.id,
        expires_at=expires_at
    )
    handler = AssignPlanHandler(session)
    
    # When
    subscription = handler.handle(command)
    
    # Then
    assert subscription.id is not None
    assert subscription.accountant_id == accountant.id
    assert subscription.plan_id == plan.id
    # Handle datetime precision in sqlite if necessary, but direct comparison should work for now
    assert subscription.expires_at == expires_at

    # Verify in DB
    db_subscription = session.exec(select(SubscriptionModel).where(SubscriptionModel.accountant_id == accountant.id)).first()
    assert db_subscription is not None
    assert db_subscription.plan_id == plan.id

def test_update_existing_subscription(session: Session):
    # Given: An accountant with an existing subscription
    accountant = AccountantModel(name="Test Accountant", cnpj="12345678000199")
    old_plan = SystemPlanModel(name="Old Plan", description="Old", price=50.0, max_clients=5)
    new_plan = SystemPlanModel(name="New Plan", description="New", price=150.0, max_clients=20)
    session.add(accountant)
    session.add(old_plan)
    session.add(new_plan)
    session.commit()
    session.refresh(accountant)
    session.refresh(old_plan)
    session.refresh(new_plan)

    old_expires_at = datetime.now() + timedelta(days=10)
    subscription = SubscriptionModel(
        accountant_id=accountant.id,
        plan_id=old_plan.id,
        expires_at=old_expires_at,
        status="active"
    )
    session.add(subscription)
    session.commit()

    new_expires_at = datetime.now() + timedelta(days=60)
    command = AssignPlanCommand(
        accountant_id=accountant.id,
        plan_id=new_plan.id,
        expires_at=new_expires_at
    )
    handler = AssignPlanHandler(session)
    
    # When
    updated_subscription = handler.handle(command)
    
    # Then
    assert updated_subscription.id == subscription.id
    assert updated_subscription.plan_id == new_plan.id
    assert updated_subscription.expires_at == new_expires_at

    # Verify in DB
    db_subscriptions = session.exec(select(SubscriptionModel).where(SubscriptionModel.accountant_id == accountant.id)).all()
    assert len(db_subscriptions) == 1
    assert db_subscriptions[0].plan_id == new_plan.id
