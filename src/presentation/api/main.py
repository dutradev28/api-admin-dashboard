from fastapi import FastAPI

app = FastAPI(title="API Admin Dashboard")

@app.get("/health")
def health_check():
    return {"status": "ok"}
