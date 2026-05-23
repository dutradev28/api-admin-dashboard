from fastapi import FastAPI
from presentation.api.v1.router import router as v1_router

app = FastAPI(title="API Admin Dashboard")

app.include_router(v1_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}
