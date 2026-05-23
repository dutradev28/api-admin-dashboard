from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel
from typing import Optional

from presentation.api.dependencies import get_current_user, get_session
from infrastructure.database.models import UserModel
from application.queries.get_accountant_dashboard import (
    GetAccountantDashboardHandler, 
    GetAccountantDashboardQuery,
    DashboardDTO
)
from application.commands.update_white_label import (
    UpdateWhiteLabelHandler,
    UpdateWhiteLabelCommand
)
from application.queries.get_public_brand_config import (
    GetPublicBrandConfigHandler,
    GetPublicBrandConfigQuery,
    PublicBrandDTO
)

router = APIRouter()

class WhiteLabelUpdateSchema(BaseModel):
    logo_url: str
    primary_color: str
    secondary_color: str

@router.get("/dashboard", response_model=DashboardDTO)
def get_dashboard(
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not current_user.accountant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an accountant"
        )
    
    query = GetAccountantDashboardQuery(accountant_id=current_user.accountant_id)
    handler = GetAccountantDashboardHandler(session)
    try:
        return handler.handle(query)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.patch("/white-label")
def update_white_label(
    update_data: WhiteLabelUpdateSchema,
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if not current_user.accountant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an accountant"
        )
    
    command = UpdateWhiteLabelCommand(
        accountant_id=current_user.accountant_id,
        logo_url=update_data.logo_url,
        primary_color=update_data.primary_color,
        secondary_color=update_data.secondary_color
    )
    handler = UpdateWhiteLabelHandler(session)
    try:
        handler.handle(command)
        return {"message": "White label configuration updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/public-brand/{accountant_id}", response_model=PublicBrandDTO)
def get_public_brand(
    accountant_id: str,
    session: Session = Depends(get_session)
):
    query = GetPublicBrandConfigQuery(accountant_id=accountant_id)
    handler = GetPublicBrandConfigHandler(session)
    try:
        return handler.handle(query)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
