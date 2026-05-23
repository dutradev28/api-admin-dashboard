import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel, StaticPool
from presentation.api.main import app
from presentation.api.dependencies import get_session, get_current_user
from infrastructure.database.models import UserModel, AccountantModel, AccountantPlanModel
from decimal import Decimal

# Setup in-memory database for testing
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture
def accountant(session: Session):
    acc = AccountantModel(id="acc-1", name="Acc 1", cnpj="111")
    session.add(acc)
    session.commit()
    return acc

@pytest.fixture
def other_accountant(session: Session):
    acc = AccountantModel(id="acc-2", name="Acc 2", cnpj="222")
    session.add(acc)
    session.commit()
    return acc

@pytest.fixture
def user(accountant: AccountantModel, session: Session):
    u = UserModel(
        id="user-1",
        email="user1@example.com",
        password_hash="hash",
        role="accountant",
        accountant_id=accountant.id
    )
    session.add(u)
    session.commit()
    return u

def test_list_plans(client: TestClient, session: Session, user: UserModel):
    # Setup
    p1 = AccountantPlanModel(id="p1", name="Plan 1", price=Decimal("100.00"), accountant_id=user.accountant_id)
    p2 = AccountantPlanModel(id="p2", name="Plan 2", price=Decimal("200.00"), accountant_id="other-acc")
    session.add(p1)
    session.add(p2)
    session.commit()

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.get("/api/v1/plans/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "p1"

def test_create_plan(client: TestClient, session: Session, user: UserModel):
    app.dependency_overrides[get_current_user] = lambda: user

    payload = {
        "name": "New Plan",
        "price": "150.50",
        "description": "A test plan"
    }
    response = client.post("/api/v1/plans/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Plan"
    assert float(data["price"]) == 150.5
    assert data["id"] is not None
    # Verify in DB
    plan_db = session.get(AccountantPlanModel, data["id"])
    assert plan_db.accountant_id == user.accountant_id

def test_update_plan(client: TestClient, session: Session, user: UserModel):
    # Setup
    p1 = AccountantPlanModel(id="p1", name="Old Name", price=Decimal("100.00"), accountant_id=user.accountant_id)
    session.add(p1)
    session.commit()

    app.dependency_overrides[get_current_user] = lambda: user

    payload = {
        "name": "Updated Name",
        "price": "120.00",
        "description": "Updated desc"
    }
    response = client.patch(f"/api/v1/plans/{p1.id}", json=payload)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"
    assert float(response.json()["price"]) == 120.0

def test_update_plan_forbidden(client: TestClient, session: Session, user: UserModel, other_accountant: AccountantModel):
    # Plan belongs to other accountant
    p1 = AccountantPlanModel(id="p1", name="Other Plan", price=Decimal("100.00"), accountant_id=other_accountant.id)
    session.add(p1)
    session.commit()

    app.dependency_overrides[get_current_user] = lambda: user

    payload = {
        "name": "Try Update",
        "price": "120.00"
    }
    response = client.patch(f"/api/v1/plans/{p1.id}", json=payload)
    assert response.status_code == 404

def test_delete_plan(client: TestClient, session: Session, user: UserModel):
    # Setup
    p1 = AccountantPlanModel(id="p1", name="To Delete", price=Decimal("100.00"), accountant_id=user.accountant_id)
    session.add(p1)
    session.commit()

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.delete(f"/api/v1/plans/{p1.id}")
    assert response.status_code == 204

    # Verify in DB
    assert session.get(AccountantPlanModel, "p1") is None

def test_delete_plan_forbidden(client: TestClient, session: Session, user: UserModel, other_accountant: AccountantModel):
    # Plan belongs to other accountant
    p1 = AccountantPlanModel(id="p1", name="Other Plan", price=Decimal("100.00"), accountant_id=other_accountant.id)
    session.add(p1)
    session.commit()

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.delete(f"/api/v1/plans/{p1.id}")
    assert response.status_code == 404
