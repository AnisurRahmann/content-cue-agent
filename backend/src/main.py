"""
CampaignCraft AI - FastAPI Main App

Backend API with Supabase integration for campaign management.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.auth.router import router as auth_router
from src.brands.router import router as brands_router
from src.campaigns.router import router as campaigns_router


# ============================================================================
# CREATE APP
# ============================================================================

app = FastAPI(
    title="CampaignCraft AI",
    description="Multi-agent marketing campaign generation API",
    version="1.0.0"
)


# ============================================================================
# FIX: Continue with CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# INCLUDE ROUTERS
# ============================================================================

app.include_router(auth_router)
app.include_router(brands_router)
app.include_router(campaigns_router)


# ============================================================================
# ROOT ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "CampaignCraft AI API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
