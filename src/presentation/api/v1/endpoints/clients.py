from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel, EmailStr
from typing import List

from presentation.api.dependencies import get_current_user, get_session
from infrastructure.database.models import UserModel
from application.commands.manage_client import (
    CreateClientCommand, CreateClientHandler,
    UpdateClientCommand, UpdateClientHandler,
    DeleteClientCommand, DeleteClientHandler
)
from application.queries.list_clients import (
    ListClientsQuery, ListClientsHandler
)

router = APIRouter()

class ClientCreateSchema(BaseModel):
    name: str
    email: EmailStr
    cnpj: str

class ClientUpdateSchema(BaseModel):
    name: str
    email: EmailStr

class ClientResponseSchema(BaseModel):
    id: str
    name: str
    email: str
    cnpj: str
    status: str

@router.get("/", response_model=List[ClientResponseSchema])
def list_clients(
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not current_user.accountant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an accountant"
        )
    
    query = ListClientsQuery(accountant_id=current_user.accountant_id)
    handler = ListClientsHandler(session)
    return handler.handle(query)

@router.post("/", response_model=ClientResponseSchema, status_code=status.HTTP_201_CREATED)
def create_client(
    client_data: ClientCreateSchema,
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not current_user.accountant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an accountant"
        )
    
    command = CreateClientCommand(
        accountant_id=current_user.accountant_id,
        name=client_data.name,
        email=client_data.email,
        cnpj=client_data.cnpj
    )
    handler = CreateClientHandler(session)
    return handler.handle(command)

@router.patch("/{client_id}", response_model=ClientResponseSchema)
def update_client(
    client_id: str,
    client_data: ClientUpdateSchema,
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not current_user.accountant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an accountant"
        )
    
    command = UpdateClientCommand(
        id=client_id,
        accountant_id=current_user.accountant_id,
        name=client_data.name,
        email=client_data.email
    )
    handler = UpdateClientHandler(session)
    try:
        return handler.handle(command)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: str,
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not current_user.accountant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an accountant"
        )
    
    command = DeleteClientCommand(
        id=client_id,
        accountant_id=current_user.accountant_id
    )
    handler = DeleteClientHandler(session)
    try:
        handler.handle(command)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
