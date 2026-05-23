import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel, StaticPool
from presentation.api.main import app
from presentation.api.dependencies import get_session, get_current_user
from infrastructure.database.models import UserModel, AccountantModel

# Setup in-memory database for testing
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

def override_get_session():
    with Session(engine) as session:
        yield session

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

def test_get_public_brand_unauthenticated(client: TestClient, session: Session):
    # Setup
    accountant = AccountantModel(
        id="acc-123",
        name="Test Acc",
        cnpj="123456789",
        primary_color="#112233",
        secondary_color="#445566"
    )
    session.add(accountant)
    session.commit()

    response = client.get("/api/v1/accountants/public-brand/acc-123")
    assert response.status_code == 200
    data = response.json()
    assert data["primary_color"] == "#112233"
    assert data["secondary_color"] == "#445566"

def test_get_dashboard_unauthorized(client: TestClient):
    response = client.get("/api/v1/accountants/dashboard")
    # OAuth2PasswordBearer returns 401 if no token is provided
    assert response.status_code == 401

def test_get_dashboard_authenticated(client: TestClient, session: Session):
    # Setup
    accountant = AccountantModel(
        id="acc-123",
        name="Test Acc",
        cnpj="123456789",
        primary_color="#112233",
        secondary_color="#445566"
    )
    user = UserModel(
        id="user-123",
        email="test@example.com",
        password_hash="hash",
        role="accountant",
        accountant_id="acc-123"
    )
    session.add(accountant)
    session.add(user)
    session.commit()

    # Override get_current_user to return our test user
    app.dependency_overrides[get_current_user] = lambda: user

    response = client.get("/api/v1/accountants/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Acc"
    assert data["brand"]["primary_color"] == "#112233"

def test_update_white_label_authenticated(client: TestClient, session: Session):
    # Setup
    accountant = AccountantModel(
        id="acc-123",
        name="Test Acc",
        cnpj="123456789",
        primary_color="#000000",
        secondary_color="#ffffff"
    )
    user = UserModel(
        id="user-123",
        email="test@example.com",
        password_hash="hash",
        role="accountant",
        accountant_id="acc-123"
    )
    session.add(accountant)
    session.add(user)
    session.commit()

    app.dependency_overrides[get_current_user] = lambda: user

    update_payload = {
        "logo_url": "http://example.com/logo.png",
        "primary_color": "#ff0000",
        "secondary_color": "#00ff00"
    }
    response = client.patch("/api/v1/accountants/white-label", json=update_payload)
    assert response.status_code == 200
    assert response.json()["message"] == "White label configuration updated successfully"

    # Verify in DB
    session.refresh(accountant)
    assert accountant.primary_color == "#ff0000"
    assert accountant.logo_url == "http://example.com/logo.png"
