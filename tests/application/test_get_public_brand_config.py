import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
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

def test_get_public_brand_config(session: Session):
    # Given: An accountant with specific branding
    accountant = AccountantModel(
        name="Public Brand Test",
        cnpj="00000000000100",
        primary_color="#FF0000",
        secondary_color="#00FF00",
        logo_url="https://example.com/logo.png"
    )
    session.add(accountant)
    session.commit()
    session.refresh(accountant)

    # When: We try to fetch the public brand config
    from application.queries.get_public_brand_config import (
        GetPublicBrandConfigQuery,
        GetPublicBrandConfigHandler,
        PublicBrandDTO
    )
    
    query = GetPublicBrandConfigQuery(accountant_id=accountant.id)
    handler = GetPublicBrandConfigHandler(session)
    result = handler.handle(query)

    # Then: We should get a DTO with only the allowed fields
    assert result.primary_color == "#FF0000"
    assert result.secondary_color == "#00FF00"
    assert result.logo_url == "https://example.com/logo.png"
    # PublicBrandDTO should only have these 3 fields
    assert len(PublicBrandDTO.model_fields) == 3
