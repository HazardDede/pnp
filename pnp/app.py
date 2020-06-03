"""The actual application wrapper around tasks and engine."""
import asyncio
from typing import Optional

from typeguard import typechecked

from pnp.api import RestAPI
from pnp.config import load_config, Configuration
from pnp.engines import DEFAULT_ENGINE, Engine
from pnp.models import tasks_to_str
from pnp.selector import PayloadSelector
from pnp.shared.exc import NoEngineError
from pnp.utils import Loggable


class Application(Loggable):
    """The wrapper that knows about tasks and engine."""

    @typechecked
    def __init__(self, config: Configuration):
        self._config = config
        if not self._config.engine:
            self._config.engine = DEFAULT_ENGINE

        self._tasks = config.tasks
        self._engine = config.engine

        self._api = None  # type: Optional[RestAPI]
        if config.api:
            self._api = RestAPI()
            self._api.create_api(
                enable_metrics=config.api.enable_metrics,
                enable_swagger=config.api.enable_swagger
            )
            self._api.add_trigger_endpoint(self._tasks)

    @property
    def api(self) -> Optional[RestAPI]:
        """Return the api that is running. If no api is available `None` is returned."""
        return self._api

    @property
    def engine(self) -> Engine:
        """Return the engine that is used to schedule and run the tasks."""
        return self._engine

    async def _run_api(self):
        if not self._api:
            return

        self._api.run_api_background(
            port=self._config.api.port
        )

    def start(self) -> None:
        """Starts the application."""
        async def _run_coros() -> None:
            await self._run_api()
            await self._engine.run(self._tasks)

        if not self._engine:
            raise NoEngineError()

        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(_run_coros())
        except KeyboardInterrupt:
            if self._api:
                self._api.shutdown()
            self._engine.stop()

    @classmethod
    def from_file(cls, file_path: str) -> 'Application':
        """
        Loads the application from a configuration file.

        Args:
            file_path (str): Where the configuration file is located.
            engine_override (str): If given overwrites the engine that is specified inside the
                configuration file.
        """
        config = load_config(str(file_path))
        PayloadSelector.instance.register_udfs(config.udfs)  # pylint: disable=no-member

        from pprint import pformat
        # pylint: disable=no-member
        cls.logger.info("API\n{}".format(config.api))
        cls.logger.info("UDFs\n{}".format(pformat(config.udfs)))
        cls.logger.info("Engine\n{}".format(config.engine))
        cls.logger.info("Configured tasks\n{}".format(tasks_to_str(config.tasks)))
        # pylint: enable=no-member
        app = Application(config)
        return app
