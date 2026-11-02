import time
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import engine, Base
from app.utils.rate_limiter import limiter
from app.routers import (
    auth_router,
    users_router,
    departments_router,
    doctors_router,
    patients_router,
    appointments_router,
    prescriptions_router,
    lab_tests_router,
    billing_router,
    pharmacy_router,
    dashboard_router,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("hospital.app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}...")
    # Initialize database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema validated and initialized.")

    # On Vercel serverless, auto-seed clean demo records into ephemeral /tmp/hospital.db
    if os.environ.get("VERCEL"):
        try:
            from scripts.seed import seed
            logger.info("Vercel serverless environment detected: seeding demo clinical data...")
            await seed()
        except Exception as e:
            logger.warning(f"Vercel auto-seed notice: {e}")

    yield
    logger.info("Shutting down application...")
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise-grade Hospital & Clinic Management System API with full RBAC, appointments, pharmacy, EHR, and billing.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Attach rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Request Logging Middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)
    logger.info(
        f"{request.method} {request.url.path} -> Status {response.status_code} in {duration_ms}ms"
    )
    return response


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred", "code": "INTERNAL_SERVER_ERROR"},
    )


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
api_v1 = settings.API_V1_STR
app.include_router(auth_router, prefix=api_v1)
app.include_router(users_router, prefix=api_v1)
app.include_router(departments_router, prefix=api_v1)
app.include_router(doctors_router, prefix=api_v1)
app.include_router(patients_router, prefix=api_v1)
app.include_router(appointments_router, prefix=api_v1)
app.include_router(prescriptions_router, prefix=api_v1)
app.include_router(lab_tests_router, prefix=api_v1)
app.include_router(billing_router, prefix=api_v1)
app.include_router(pharmacy_router, prefix=api_v1)
app.include_router(dashboard_router, prefix=api_v1)

# Ensure upload directory exists and mount static / uploads
upload_dir = settings.effective_upload_dir
try:
    os.makedirs(upload_dir, exist_ok=True)
except Exception:
    pass
os.makedirs("static", exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENV,
    }


@app.get("/", include_in_schema=False)
async def root():
    # If interactive frontend exists, serve it; else redirect to /docs
    index_file = os.path.join("static", "app", "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Welcome to Hospital Management API", "docs": "/docs", "health": "/health"}
