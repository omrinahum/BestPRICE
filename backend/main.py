# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.routers import search_router, offer_router, auth_router, user_router, deals_router
from backend.utils.error import ValidationError, NotFoundError, ExternalAPIError
from backend.scheduler import start_scheduler, stop_scheduler

# Global scheduler instance
scheduler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Starts the background scheduler on startup and stops it on shutdown.
    """
    global scheduler
    # Startup: Start the scheduler
    scheduler = start_scheduler()
    yield
    # Shutdown: Stop the scheduler
    stop_scheduler(scheduler)

app = FastAPI(lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Exception Handlers through FASTAPI for endpoint
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})

@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(ExternalAPIError)
async def external_api_exception_handler(request: Request, exc: ExternalAPIError):
    return JSONResponse(status_code=502, content={"detail": str(exc)})

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(search_router.router, prefix="/search", tags=["search"])
app.include_router(offer_router.router, prefix="/offers", tags=["offers"])
app.include_router(auth_router.router, prefix="/auth", tags=["authentication"])
app.include_router(user_router.router, prefix="/user", tags=["user"])
app.include_router(deals_router.router, prefix="/deals", tags=["deals"])

