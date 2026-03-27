"""
Main FastAPI application.
EEntry point for API server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chronosdb.api.rest import tenants, jobs, health

# Create FastAPI app
app = FastAPI(
    title="ChronosDB",
    description="Durable async job execution engine with AI-powered retry",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers
app.include_router(health.router)  # /health, /ready
app.include_router(tenants.router, prefix="/api/v1")  # /api/v1/tenants
app.include_router(jobs.router, prefix="/api/v1")     # /api/v1/jobs


@app.get("/")
async def root():
    """
    Root endpoint - shows API info.
    
    Access at: http://localhost:8000/
    """
    return {
        "name": "ChronosDB",
        "version": "0.1.0",
        "status": "running",
        "docs": "http://localhost:8000/docs"
    }


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print("🚀 ChronosDB API starting...")
    print("📖 Docs available at: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print("👋 ChronosDB API shutting down...")