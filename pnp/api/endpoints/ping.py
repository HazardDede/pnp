"""Contains a ping endpoint."""

from fastapi import FastAPI
from starlette.responses import PlainTextResponse

from .base import Endpoint


class Ping(Endpoint):
    """Ping endpoint. When requested just returns a simple pong."""

    async def endpoint(self) -> str:
        """Returns 'pong' when requested. Use this as a basic health endpoint.
        This will not do any additional checks (like database access, ...)
        but accessibility only."""
        return "pong"

    def attach(self, fastapi: FastAPI) -> None:
        """Attach the endpoint to the serving component."""
        fastapi.get(
            path="/ping",
            response_class=PlainTextResponse
        )(self.endpoint)
