
import pytest
from fastapi import HTTPException
from backend.utils.error import handle_api_errors, ValidationError, NotFoundError, ExternalAPIError

@handle_api_errors
async def _ok():
    """A dummy endpoint that returns normally."""
    return "OK"

@handle_api_errors
async def _raise_validation():
    """Raises ValidationError and should map to HTTP 422."""
    raise ValidationError("bad")

@handle_api_errors
async def _raise_not_found():
    """Raises NotFoundError and should map to HTTP 404."""
    raise NotFoundError("missing")

@handle_api_errors
async def _raise_external():
    """Raises ExternalAPIError and should map to HTTP 502."""
    raise ExternalAPIError("downstream")

@handle_api_errors
async def _raise_unknown():
    """Raises unknown Exception and should map to HTTP 500."""
    raise RuntimeError("wtf")

import pytest

@pytest.mark.asyncio
async def test_handle_api_errors_ok():
    """Decorator: passes through normal return value."""
    assert await _ok() == "OK"

@pytest.mark.asyncio
async def test_handle_api_errors_validation():
    """Decorator: converts ValidationError -> HTTP 422."""
    with pytest.raises(HTTPException) as ei:
        await _raise_validation()
    assert ei.value.status_code == 422

@pytest.mark.asyncio
async def test_handle_api_errors_not_found():
    """Decorator: converts NotFoundError -> HTTP 404."""
    with pytest.raises(HTTPException) as ei:
        await _raise_not_found()
    assert ei.value.status_code == 404

@pytest.mark.asyncio
async def test_handle_api_errors_external():
    """Decorator: converts ExternalAPIError -> HTTP 502."""
    with pytest.raises(HTTPException) as ei:
        await _raise_external()
    assert ei.value.status_code == 502

@pytest.mark.asyncio
async def test_handle_api_errors_unknown():
    """Decorator: converts unknown exceptions -> HTTP 500."""
    with pytest.raises(HTTPException) as ei:
        await _raise_unknown()
    assert ei.value.status_code == 500
