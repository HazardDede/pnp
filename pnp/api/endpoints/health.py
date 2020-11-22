"""Contains a health endpoint."""

from fastapi import FastAPI

from pnp.api.models import HealthResponse
from .base import Endpoint


class Health(Endpoint):
    """When requested returns a health response with the general health of the application.
       Right now this does not perform any health checks, but it will in the future."""

    async def endpoint(self) -> HealthResponse:
        """When requested returns a health response with the general health of the application.
        Right now this does not perform any health checks, but it will in the future."""
        return HealthResponse()

    def attach(self, fastapi: FastAPI) -> None:
        """Attach the endpoint to the serving component."""
        fastapi.get(
            path="/health",
            response_model=HealthResponse
        )(self.endpoint)
