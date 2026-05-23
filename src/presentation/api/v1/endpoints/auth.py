from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel

from presentation.api.dependencies import get_session
from application.queries.login import LoginHandler, LoginQuery
from application.commands.sign_up import SignUpHandler, SignUpCommand
from application.commands.forgot_password import ForgotPasswordHandler, ForgotPasswordCommand
from application.commands.reset_password import ResetPasswordHandler, ResetPasswordCommand

router = APIRouter()

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ResetPasswordSchema(BaseModel):
    token: str
    new_password: str

@router.post("/login", response_model=TokenResponse)
def login(query: LoginQuery, session: Session = Depends(get_session)):
    handler = LoginHandler(session)
    try:
        token = handler.handle(query)
        return {"access_token": token}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(command: SignUpCommand, session: Session = Depends(get_session)):
    handler = SignUpHandler(session)
    try:
        accountant = handler.handle(command)
        return {"message": "Account created successfully", "accountant_id": str(accountant.id)}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/forgot-password")
def forgot_password(command: ForgotPasswordCommand, session: Session = Depends(get_session)):
    handler = ForgotPasswordHandler(session)
    try:
        token = handler.handle(command)
        return {"message": "Recovery token generated", "token": token}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/reset-password")
def reset_password(data: ResetPasswordSchema, session: Session = Depends(get_session)):
    command = ResetPasswordCommand(token=data.token, new_password=data.new_password)
    handler = ResetPasswordHandler(session)
    try:
        handler.handle(command)
        return {"message": "Password reset successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
