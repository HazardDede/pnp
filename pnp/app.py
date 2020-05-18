"""The actual application wrapper around tasks and engine."""
import asyncio
from typing import Optional, Any

from pnp.api import run_api_background, create_api
from pnp.config import load_config, Configuration
from pnp.engines import DEFAULT_ENGINES
from pnp.models import tasks_to_str
from pnp.selector import PayloadSelector
from pnp.shared.exc import NoEngineError
from pnp.utils import Loggable
from pnp.validator import Validator


class Application(Loggable):
    """The wrapper that knows about tasks and engine."""
    def __init__(self, config: Configuration):
        Validator.is_instance(Configuration, config=config)

        self._config = config
        self._tasks = config.tasks
        self._engine = config.engine or DEFAULT_ENGINES['async']()
        self._api = config.api
        self._api_server = None  # type: Any

    async def _run_tasks(self) -> None:
        if self._api:
            self._api_server = run_api_background(
                api=create_api(
                    enable_metrics=self._api.enable_metrics,
                    enable_swagger=self._api.enable_swagger
                ),
                port=self._api.port
            )
        await self._engine.run(self._tasks)

    def start(self) -> None:
        """Starts the application."""
        if not self._engine:
            raise NoEngineError()

        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self._run_tasks())
        except KeyboardInterrupt:
            if self._api_server:
                self._api_server.close()
            self._engine.stop()

    @classmethod
    def from_file(cls, file_path: str, engine_override: Optional[str] = None) -> 'Application':
        """
        Loads the application from a configuration file.

        Args:
            file_path (str): Where the configuration file is located.
            engine_override (str): If given overwrites the engine that is specified inside the
                configuration file.
        """
        Validator.one_of(
            list(DEFAULT_ENGINES.keys()),
            allow_none=True,
            engine_override=engine_override
        )

        config = load_config(file_path)
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
