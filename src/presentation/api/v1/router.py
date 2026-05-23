from fastapi import APIRouter
from presentation.api.v1.endpoints import accountants

router = APIRouter()

router.include_router(accountants.router, prefix="/accountants", tags=["accountants"])

@router.get("/ping")
def ping():
    return {"message": "pong"}
