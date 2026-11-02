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

# Base directory for absolute path resolution across local and serverless environments
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")


class PathNormalizationMiddleware:
    """
    Normalizes incoming request paths for Vercel Serverless environment.
    Strips leading /api/index.py or /api/index prefixes so FastAPI routes match cleanly.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            path = scope.get("path", "")
            for prefix in ("/api/index.py", "/api/index"):
                if path.startswith(prefix):
                    new_path = path[len(prefix):]
                    if not new_path or not new_path.startswith("/"):
                        new_path = "/" + new_path.lstrip("/")
                    scope["path"] = new_path
                    if "raw_path" in scope:
                        scope["raw_path"] = new_path.encode("utf-8")
                    break
        await self.app(scope, receive, send)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}...")
    from app.database import init_db
    await init_db()
    logger.info("Database schema validated and initialized.")
    yield
    logger.info("Shutting down application...")
    await engine.dispose()

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


# Path Normalization Middleware for Vercel
app.add_middleware(PathNormalizationMiddleware)

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

try:
    os.makedirs(STATIC_DIR, exist_ok=True)
except Exception:
    pass

app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENV,
    }


@app.get("/", include_in_schema=False)
@app.get("/api/index.py", include_in_schema=False)
@app.get("/api/index", include_in_schema=False)
async def root():
    # If interactive frontend exists, serve it; else redirect to /docs
    index_file = os.path.join(STATIC_DIR, "app", "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file, media_type="text/html")
    fallback_index = os.path.join("static", "app", "index.html")
    if os.path.exists(fallback_index):
        return FileResponse(fallback_index, media_type="text/html")
    return {"message": "Welcome to Hospital Management API", "docs": "/docs", "health": "/health"}
