import pytest
from decimal import Decimal
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from infrastructure.database.models import SystemPlanModel
# These will fail to import initially
from application.commands.create_system_plan import CreateSystemPlanCommand, CreateSystemPlanHandler

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

def test_create_system_plan_command(session: Session):
    # Given
    command = CreateSystemPlanCommand(
        name="Premium Plan",
        description="A premium plan with more features",
        price=Decimal("99.90"),
        max_clients=100
    )
    handler = CreateSystemPlanHandler(session)
    
    # When
    plan = handler.handle(command)
    
    # Then
    assert plan.id is not None
    assert plan.name == "Premium Plan"
    assert plan.description == "A premium plan with more features"
    assert plan.price == Decimal("99.90")
    assert plan.max_clients == 100
    assert plan.is_active is True
    
    # Verify in DB
    db_plan = session.get(SystemPlanModel, plan.id)
    assert db_plan is not None
    assert db_plan.name == "Premium Plan"
