from fastapi import APIRouter
from presentation.api.v1.endpoints import accountants, clients, plans, auth

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(accountants.router, prefix="/accountants", tags=["accountants"])
router.include_router(clients.router, prefix="/clients", tags=["clients"])
router.include_router(plans.router, prefix="/plans", tags=["plans"])

@router.get("/ping")
def ping():
    return {"message": "pong"}
