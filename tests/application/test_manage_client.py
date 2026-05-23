import pytest
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool
from infrastructure.database.models import AccountantModel, ClientModel
from application.commands.manage_client import (
    CreateClientCommand, CreateClientHandler,
    UpdateClientCommand, UpdateClientHandler,
    DeleteClientCommand, DeleteClientHandler
)
from application.queries.list_clients import ListClientsQuery, ListClientsHandler

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

@pytest.fixture(name="accountant1")
def accountant1_fixture(session: Session):
    acc = AccountantModel(name="Acc 1", cnpj="11111111000111")
    session.add(acc)
    session.commit()
    session.refresh(acc)
    return acc

@pytest.fixture(name="accountant2")
def accountant2_fixture(session: Session):
    acc = AccountantModel(name="Acc 2", cnpj="22222222000122")
    session.add(acc)
    session.commit()
    session.refresh(acc)
    return acc

def test_create_client(session: Session, accountant1: AccountantModel):
    # Given
    command = CreateClientCommand(
        accountant_id=accountant1.id,
        name="Client 1",
        email="client1@test.com",
        cnpj="33333333000133"
    )
    handler = CreateClientHandler(session)
    
    # When
    client = handler.handle(command)
    
    # Then
    assert client.id is not None
    assert client.accountant_id == accountant1.id
    assert client.name == "Client 1"
    
    # Verify in DB
    db_client = session.get(ClientModel, client.id)
    assert db_client is not None
    assert db_client.name == "Client 1"

def test_update_client_success(session: Session, accountant1: AccountantModel):
    # Given
    client = ClientModel(accountant_id=accountant1.id, name="Old Name", email="old@test.com", cnpj="123")
    session.add(client)
    session.commit()
    session.refresh(client)
    
    command = UpdateClientCommand(
        id=client.id,
        accountant_id=accountant1.id,
        name="New Name",
        email="new@test.com"
    )
    handler = UpdateClientHandler(session)
    
    # When
    updated_client = handler.handle(command)
    
    # Then
    assert updated_client.name == "New Name"
    assert updated_client.email == "new@test.com"

def test_update_client_isolation_failure(session: Session, accountant1: AccountantModel, accountant2: AccountantModel):
    # Given
    client_of_acc1 = ClientModel(accountant_id=accountant1.id, name="Acc1 Client", email="acc1@test.com", cnpj="123")
    session.add(client_of_acc1)
    session.commit()
    session.refresh(client_of_acc1)
    
    # Acc2 tries to update Acc1's client
    command = UpdateClientCommand(
        id=client_of_acc1.id,
        accountant_id=accountant2.id,
        name="Stolen Update",
        email="stolen@test.com"
    )
    handler = UpdateClientHandler(session)
    
    # When / Then
    with pytest.raises(ValueError, match="Client not found or does not belong to this accountant"):
        handler.handle(command)

def test_delete_client_success(session: Session, accountant1: AccountantModel):
    # Given
    client = ClientModel(accountant_id=accountant1.id, name="To Delete", email="del@test.com", cnpj="123")
    session.add(client)
    session.commit()
    session.refresh(client)
    
    command = DeleteClientCommand(
        id=client.id,
        accountant_id=accountant1.id
    )
    handler = DeleteClientHandler(session)
    
    # When
    handler.handle(command)
    
    # Then
    db_client = session.get(ClientModel, client.id)
    assert db_client is None

def test_delete_client_isolation_failure(session: Session, accountant1: AccountantModel, accountant2: AccountantModel):
    # Given
    client_of_acc1 = ClientModel(accountant_id=accountant1.id, name="Acc1 Client", email="acc1@test.com", cnpj="123")
    session.add(client_of_acc1)
    session.commit()
    session.refresh(client_of_acc1)
    
    # Acc2 tries to delete Acc1's client
    command = DeleteClientCommand(
        id=client_of_acc1.id,
        accountant_id=accountant2.id
    )
    handler = DeleteClientHandler(session)
    
    # When / Then
    with pytest.raises(ValueError, match="Client not found or does not belong to this accountant"):
        handler.handle(command)

def test_list_clients_filtering(session: Session, accountant1: AccountantModel, accountant2: AccountantModel):
    # Given
    c1 = ClientModel(accountant_id=accountant1.id, name="C1", email="c1@a1.com", cnpj="1")
    c2 = ClientModel(accountant_id=accountant1.id, name="C2", email="c2@a1.com", cnpj="2")
    c3 = ClientModel(accountant_id=accountant2.id, name="C3", email="c3@a2.com", cnpj="3")
    session.add_all([c1, c2, c3])
    session.commit()
    
    query = ListClientsQuery(accountant_id=accountant1.id)
    handler = ListClientsHandler(session)
    
    # When
    results = handler.handle(query)
    
    # Then
    assert len(results) == 2
    assert all(c.accountant_id == accountant1.id for c in results)
    assert {c.name for c in results} == {"C1", "C2"}
