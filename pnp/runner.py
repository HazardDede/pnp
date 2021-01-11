"""Contains runner to run an application."""

import asyncio
import os
import signal

import uvicorn

from pnp.api import APINotConfiguredError
from pnp.app import Application
from pnp.utils import Loggable


class Runner(Loggable):
    """Runner to run a basic non-api application."""
    def __init__(self, app: Application):
        self.app = app

    async def _main_loop(self) -> None:
        while self.app.engine.is_running:
            await asyncio.sleep(0.1)

    def run(self) -> None:
        """Run the application."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.app.engine.start(self.app.tasks))
        try:
            loop.run_until_complete(self._main_loop())
        except KeyboardInterrupt:
            try:
                self.logger.info(
                    "Attempting graceful shutdown, press Ctrl+C again to exit forcefully..."
                )
                loop.run_until_complete(self.app.engine.stop())
            except KeyboardInterrupt:
                self.logger.info("Forceful exit")

    @classmethod
    def choose_runner(cls, app: Application) -> 'Runner':
        """Factory method to choose the correct runner for the given application."""
        if app.api is not None:
            return APIAwareRunner(app)
        return cls(app)


class APIAwareRunner(Runner):
    """Runner that knows how to handle a fastapi api."""
    async def _on_engine_stopped(self):
        # The only way I know to programmatically stop uvicorn politely
        # without messing with uvicorn internals
        os.kill(os.getpid(), signal.SIGTERM)

    def run(self):
        api = self.app.api
        if not api:
            raise APINotConfiguredError()
        engine = self.app.engine
        engine.on_stopped_callback = self._on_engine_stopped

        @api.fastapi.on_event("startup")  # type: ignore
        async def _on_startup() -> None:
            await engine.start(self.app.tasks)

        @api.fastapi.on_event("shutdown")  # type: ignore
        async def _on_shutdown() -> None:
            await engine.stop()

        uvicorn.run(
            api.fastapi,
            host="0.0.0.0",
            port=self.app.config.api.port,
            log_config=None,
            log_level="debug"
        )
