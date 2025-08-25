import logging
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

class ExternalAPIError(Exception): pass
class NotFoundError(Exception): pass
class ValidationError(Exception): pass

def handle_api_errors(func):
    """
    Decorator for FastAPI endpoints to handle and log errors consistently.
    """
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValidationError as e:
            logging.error(f"Validation error: {e}")
            raise HTTPException(status_code=422, detail=str(e))
        except NotFoundError as e:
            logging.error(f"Not found: {e}")
            raise HTTPException(status_code=404, detail=str(e))
        except ExternalAPIError as e:
            logging.error(f"External API error: {e}")
            raise HTTPException(status_code=502, detail="External service error: " + str(e))
        except SQLAlchemyError as e:
            logging.error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail="Database error occurred. Please try again later.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred. Please contact support.")
    return wrapper