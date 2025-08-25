# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.routers import search_router, offer_router
from backend.utils.error import ValidationError, NotFoundError, ExternalAPIError

app = FastAPI()

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

