from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.database.init_db import init_db
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.api.driver import router as driver_router
from app.api.student import router as student_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database tables on startup
    init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent bus arrival delay prediction system for Sri Eshwar College of Engineering, Coimbatore.",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=getattr(exc, "headers", None)
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    err_msgs = []
    for err in exc.errors():
        loc = " -> ".join([str(l) for l in err.get("loc", []) if l != "body"])
        msg = err.get("msg", "Invalid value")
        err_msgs.append(f"{loc}: {msg}" if loc else msg)
    detail_str = "; ".join(err_msgs) if err_msgs else "Invalid input data"
    return JSONResponse(
        status_code=422,
        content={"detail": detail_str, "errors": exc.errors()}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=getattr(exc, "headers", None)
        )
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Internal Server Error: {str(exc)}",
            "error": "Internal Server Error",
            "message": str(exc),
            "path": request.url.path
        }
    )

# Include core routers under /api and /api/v1
for prefix in ["/api", "/api/v1"]:
    app.include_router(health_router, prefix=prefix)
    app.include_router(auth_router, prefix=prefix)
    app.include_router(admin_router, prefix=prefix)
    app.include_router(driver_router, prefix=prefix)
    app.include_router(student_router, prefix=prefix)

# Also include root-level /auth, /admin, /driver, /student for direct access
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(driver_router)
app.include_router(student_router)

@app.get("/")
def root():
    return {
        "app": "BusFlow",
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "institution": settings.INSTITUTION_NAME,
        "docs": "/api/docs",
        "health": "/api/health"
    }
