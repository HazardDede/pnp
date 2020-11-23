"""Contains api models that are globally useful."""
from pydantic import BaseModel  # pylint: disable=no-name-in-module
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK


class _EmptyResponse:
    """An empty json response."""
    def __call__(self, status_code: int = HTTP_200_OK) -> JSONResponse:
        return JSONResponse(status_code=status_code, content={})


EmptyResponse = _EmptyResponse()


class HealthResponse(BaseModel):
    """Basic health response."""

    success: bool = True
