"""
FastAPI Main App

REST API for campaign management and workflow execution.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.campaigns import router as campaigns_router


app = FastAPI(
    title="ContentCued Marketing Agent API",
    description="Multi-agent campaign generation system",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(campaigns_router, prefix="/api/v1", tags=["campaigns"])


@app.get("/")
def root():
    return {"message": "ContentCued Marketing Agent API", "version": "0.1.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
