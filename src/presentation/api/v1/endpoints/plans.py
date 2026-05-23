from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional

from presentation.api.dependencies import get_current_user, get_session
from infrastructure.database.models import UserModel
from application.commands.manage_accountant_plan import (
    CreateAccountantPlanCommand, CreateAccountantPlanHandler,
    UpdateAccountantPlanCommand, UpdateAccountantPlanHandler,
    DeleteAccountantPlanCommand, DeleteAccountantPlanHandler
)
from application.queries.list_accountant_plans import (
    ListAccountantPlansQuery, ListAccountantPlansHandler,
    AccountantPlanDTO
)

router = APIRouter()

class PlanCreateSchema(BaseModel):
    name: str
    price: Decimal
    description: Optional[str] = None

class PlanUpdateSchema(BaseModel):
    name: str
    price: Decimal
    description: Optional[str] = None

@router.get("/", response_model=List[AccountantPlanDTO])
def list_plans(
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not current_user.accountant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an accountant"
        )
    
    query = ListAccountantPlansQuery(accountant_id=current_user.accountant_id)
    handler = ListAccountantPlansHandler(session)
    return handler.handle(query)

@router.post("/", response_model=AccountantPlanDTO, status_code=status.HTTP_201_CREATED)
def create_plan(
    plan_data: PlanCreateSchema,
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not current_user.accountant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an accountant"
        )
    
    command = CreateAccountantPlanCommand(
        accountant_id=current_user.accountant_id,
        name=plan_data.name,
        price=plan_data.price,
        description=plan_data.description
    )
    handler = CreateAccountantPlanHandler(session)
    result = handler.handle(command)
    return AccountantPlanDTO(
        id=result.id,
        name=result.name,
        price=result.price,
        description=result.description
    )

@router.patch("/{plan_id}", response_model=AccountantPlanDTO)
def update_plan(
    plan_id: str,
    plan_data: PlanUpdateSchema,
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not current_user.accountant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an accountant"
        )
    
    command = UpdateAccountantPlanCommand(
        id=plan_id,
        accountant_id=current_user.accountant_id,
        name=plan_data.name,
        price=plan_data.price,
        description=plan_data.description
    )
    handler = UpdateAccountantPlanHandler(session)
    try:
        result = handler.handle(command)
        return AccountantPlanDTO(
            id=result.id,
            name=result.name,
            price=result.price,
            description=result.description
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(
    plan_id: str,
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not current_user.accountant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an accountant"
        )
    
    command = DeleteAccountantPlanCommand(
        id=plan_id,
        accountant_id=current_user.accountant_id
    )
    handler = DeleteAccountantPlanHandler(session)
    try:
        handler.handle(command)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
