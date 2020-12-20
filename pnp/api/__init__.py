"""Global pnp api toolkit."""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator

from fastapi import FastAPI
from uvicorn.config import Config
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

    @asynccontextmanager
    async def run_api_background(self, port: int = 9999) -> AsyncGenerator[None, None]:
        """
        Runs the api application in the background.
        The control will be returned to the caller.
        If the caller gives back control the api will terminated.
        Useful for testing and _NOT_ for production use.
        """

        api = self._assert_api()
        port = int(port)
        self.port = port

        cfg = Config(app=api, host="0.0.0.0", port=port, log_config=None)
        self._fastapi_server = Server(config=cfg)

        # We need to tweak shutdown to mark the server as not started
        original_shutdown = self._fastapi_server.shutdown

        async def shutdown(sockets=None):  # type: ignore
            await original_shutdown(sockets)
            assert self._fastapi_server
            self._fastapi_server.started = False
        self._fastapi_server.shutdown = shutdown

        # Do not use signal handlers - these will block the KeyboardInterrupt in app.py
        # We need to remember this on shutdown
        self._fastapi_server.install_signal_handlers = lambda *args: None
        loop = asyncio.get_event_loop()
        loop.create_task(self._fastapi_server.serve())

        try:
            yield
        finally:
            # We do what the signalhandler would normally do...
            self._fastapi_server.should_exit = True
            while self._fastapi_server.started:
                await asyncio.sleep(0.1)

            self.port = None
            self._fastapi_server = None
