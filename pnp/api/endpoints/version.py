"""Contains a version endpoint."""

import sys

from fastapi import FastAPI
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from pnp import __version__ as __pnp_version__
from .base import Endpoint


class VersionResponse(BaseModel):
    """Version response."""

    version: str = __pnp_version__
    python: str = sys.version


class Version(Endpoint):
    """When requested returns the current pnp and python version."""

    async def _endpoint(self) -> VersionResponse:
        """Returns the current pnp and python version."""
        return VersionResponse()

    def attach(self, fastapi: FastAPI) -> None:
        """Attach the endpoint to the serving component."""
        fastapi.get(
            path="/version",
            response_model=VersionResponse
        )(self._endpoint)
