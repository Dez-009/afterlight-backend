from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import uuid
from contextlib import asynccontextmanager

from app.config import settings
from app.middleware.auth import AuthMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.api.v1 import personas, auth, cultural, planning, admin

# Global variables for request tracking
request_count = 0
start_time = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting AfterLight FastAPI Backend...")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    print(f"🔐 JWT Secret: {'*' * 10 if settings.JWT_SECRET else 'NOT SET'}")
    print(f"🗄️ Database: {settings.DATABASE_URL[:20]}..." if settings.DATABASE_URL else "NOT SET")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down AfterLight Backend...")
    print(f"📈 Total requests processed: {request_count}")
    print(f"⏱️ Uptime: {time.time() - start_time:.2f} seconds")

# Create FastAPI app
app = FastAPI(
    title="AfterLight API",
    description="Premium digital platform for memorial planning and celebration of life",
    version="1.1.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware for production
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# Add custom middleware
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthMiddleware)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = str(uuid.uuid4())
    
    # Log the error (in production, send to monitoring service)
    print(f"❌ Error {request_id}: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "code": "INTERNAL_ERROR",
            "request_id": request_id,
            "timestamp": time.time()
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    global request_count
    request_count += 1
    
    try:
        # Basic health check - just return success
        health_data = {
            "success": True,
            "status": "healthy",
            "timestamp": time.time(),
            "uptime": time.time() - start_time,
            "requests_processed": request_count,
            "version": "1.1.0",
            "environment": settings.ENVIRONMENT
        }
        
        print(f"✅ Health check passed - Request #{request_count}")
        return health_data
        
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
        )

# API information endpoint
@app.get("/")
async def root():
    return {
        "success": True,
        "message": "AfterLight API - Premium Memorial Planning Platform",
        "version": "1.1.0",
        "docs": "/docs" if settings.ENVIRONMENT != "production" else None,
        "health": "/health"
    }

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(personas.router, prefix="/api/v1/personas", tags=["Personas"])
app.include_router(cultural.router, prefix="/api/v1/cultural", tags=["Cultural"])
app.include_router(planning.router, prefix="/api/v1/planning", tags=["Planning"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )
