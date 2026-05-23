import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from infrastructure.database.models import AccountantModel, SystemPlanModel, SubscriptionModel
from application.queries.get_accountant_dashboard import (
    GetAccountantDashboardQuery,
    GetAccountantDashboardHandler,
    DashboardDTO
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

def test_get_accountant_dashboard_query(session: Session):
    # Given: An accountant, a plan, and an active subscription
    accountant = AccountantModel(
        name="Tech Accounting",
        cnpj="12345678000199",
        primary_color="#123456",
        secondary_color="#654321"
    )
    plan = SystemPlanModel(
        name="Pro Plan",
        description="Professional Plan",
        price=299.90,
        max_clients=100
    )
    session.add(accountant)
    session.add(plan)
    session.commit()
    session.refresh(accountant)
    session.refresh(plan)

    expires_at = datetime.now() + timedelta(days=365)
    subscription = SubscriptionModel(
        accountant_id=accountant.id,
        plan_id=plan.id,
        expires_at=expires_at,
        status="active"
    )
    session.add(subscription)
    session.commit()

    query = GetAccountantDashboardQuery(accountant_id=accountant.id)
    handler = GetAccountantDashboardHandler(session)
    
    # When
    dashboard_data = handler.handle(query)
    
    # Then
    assert isinstance(dashboard_data, DashboardDTO)
    assert dashboard_data.name == "Tech Accounting"
    assert dashboard_data.cnpj == "12345678000199"
    assert dashboard_data.brand.primary_color == "#123456"
    assert dashboard_data.brand.secondary_color == "#654321"
    assert dashboard_data.subscription is not None
    assert dashboard_data.subscription.plan_name == "Pro Plan"
    assert dashboard_data.subscription.status == "active"
    assert dashboard_data.subscription.expires_at == expires_at
