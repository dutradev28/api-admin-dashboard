import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel, StaticPool
from presentation.api.main import app
from presentation.api.dependencies import get_session, get_current_user
from infrastructure.database.models import UserModel, AccountantModel, ClientModel

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

def test_list_clients(client: TestClient, session: Session, user: UserModel):
    # Setup
    c1 = ClientModel(id="c1", name="Client 1", email="c1@ex.com", cnpj="c111", accountant_id=user.accountant_id)
    c2 = ClientModel(id="c2", name="Client 2", email="c2@ex.com", cnpj="c222", accountant_id="other-acc")
    session.add(c1)
    session.add(c2)
    session.commit()

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.get("/api/v1/clients/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "c1"

def test_create_client(client: TestClient, session: Session, user: UserModel):
    app.dependency_overrides[get_current_user] = lambda: user

    payload = {
        "name": "New Client",
        "email": "new@client.com",
        "cnpj": "999888777"
    }
    response = client.post("/api/v1/clients/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Client"
    assert data["id"] is not None

    # Verify in DB
    client_db = session.get(ClientModel, data["id"])
    assert client_db.accountant_id == user.accountant_id

def test_update_client(client: TestClient, session: Session, user: UserModel):
    # Setup
    c1 = ClientModel(id="c1", name="Old Name", email="old@ex.com", cnpj="c111", accountant_id=user.accountant_id)
    session.add(c1)
    session.commit()

    app.dependency_overrides[get_current_user] = lambda: user

    payload = {
        "name": "Updated Name",
        "email": "updated@ex.com"
    }
    response = client.patch(f"/api/v1/clients/{c1.id}", json=payload)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"

def test_update_client_forbidden(client: TestClient, session: Session, user: UserModel, other_accountant: AccountantModel):
    # Client belongs to other accountant
    c1 = ClientModel(id="c1", name="Other Client", email="other@ex.com", cnpj="c111", accountant_id=other_accountant.id)
    session.add(c1)
    session.commit()

    app.dependency_overrides[get_current_user] = lambda: user

    payload = {
        "name": "Try Update",
        "email": "try@ex.com"
    }
    response = client.patch(f"/api/v1/clients/{c1.id}", json=payload)
    assert response.status_code == 404 # Handler raises ValueError which becomes 404

def test_delete_client(client: TestClient, session: Session, user: UserModel):
    # Setup
    c1 = ClientModel(id="c1", name="To Delete", email="del@ex.com", cnpj="c111", accountant_id=user.accountant_id)
    session.add(c1)
    session.commit()

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.delete(f"/api/v1/clients/{c1.id}")
    assert response.status_code == 204

    # Verify in DB
    assert session.get(ClientModel, "c1") is None

def test_delete_client_forbidden(client: TestClient, session: Session, user: UserModel, other_accountant: AccountantModel):
    # Client belongs to other accountant
    c1 = ClientModel(id="c1", name="Other Client", email="other@ex.com", cnpj="c111", accountant_id=other_accountant.id)
    session.add(c1)
    session.commit()

    app.dependency_overrides[get_current_user] = lambda: user

    response = client.delete(f"/api/v1/clients/{c1.id}")
    assert response.status_code == 404
