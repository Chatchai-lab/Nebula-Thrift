from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import snapshots, accounts

app = FastAPI(
    title="Nebula Thrift API",
    description="AI-powered Cloud Cost Optimizer",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(snapshots.router)
app.include_router(accounts.router)


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "nebula-thrift"}
