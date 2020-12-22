"""Global pnp api toolkit."""

import logging
from typing import Optional

from fastapi import FastAPI
from uvicorn.main import Server

from pnp import __version__
from pnp.api.endpoints import Ping, Health, SetLogLevel, PrometheusExporter, Version
from pnp.utils import Singleton

_LOGGER = logging.getLogger(__name__)


class APIError(RuntimeError):
    """Raised when some api error is experienced."""

    DEFAULT_MESSAGE = "Internal API error."

    def __init__(self, message: Optional[str] = None):
        super().__init__(message or self.DEFAULT_MESSAGE)


class APINotConfiguredError(APIError):
    """Raised when the api is not configured / enabled, but is necessary to perform a
    task."""

    DEFAULT_MESSAGE = "API is not configured, but is required to perform this task."


class APINotInitialized(APIError):
    """Raised when the api not initialized properly."""

    DEFAULT_MESSAGE = "API is not initialized properly. Try to `RestAPI.create_api(...)` first."


class RestAPI(Singleton):
    """API singleton."""

    def __init__(self) -> None:  # pylint: disable=super-init-not-called
        self.fastapi: Optional[FastAPI] = None
        self.port: Optional[int] = None
        self._fastapi_server: Optional[Server] = None

    def _assert_api(self) -> FastAPI:
        if not self.fastapi:
            raise APINotInitialized()
        return self.fastapi

    @property
    def enabled(self) -> bool:
        """Return True if the api is enabled; otherwise False."""
        return self.fastapi is not None

    def create_api(
        self, app_name: str = "pnp", enable_metrics: bool = True
    ) -> None:
        """
        Creates a fastAPI application to serve api requests.
        """
        self.fastapi = FastAPI(title=app_name, version=__version__)

        Ping().attach(self.fastapi)
        Health().attach(self.fastapi)
        SetLogLevel().attach(self.fastapi)
        Version().attach(self.fastapi)

        if bool(enable_metrics):
            PrometheusExporter(app_name).attach(self.fastapi)
