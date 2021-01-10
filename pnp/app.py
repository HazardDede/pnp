"""The actual application wrapper around tasks and engine."""
from typing import Optional

from typeguard import typechecked

from pnp.api import RestAPI
from pnp.api.endpoints import Trigger
from pnp.config import load_config, Configuration
from pnp.engines import DEFAULT_ENGINE, Engine
from pnp.models import TaskSet
from pnp.selector import PayloadSelector
from pnp.utils import Loggable, ReprMixin


class Application(Loggable, ReprMixin):
    """The wrapper that knows about tasks and engine."""

    __REPR_FIELDS__ = ['_api', '_engine', '_tasks']

    @typechecked
    def __init__(self, config: Configuration):
        self.config = config
        if not self.config.engine:
            self.config.engine = DEFAULT_ENGINE

        self._tasks = config.tasks
        self._engine = config.engine

        self._api = None  # type: Optional[RestAPI]
        if config.api:
            self._api = RestAPI()
            self._api.create_api(
                enable_metrics=config.api.enable_metrics,
            )
            Trigger(config.tasks).attach(self._api.fastapi)

    @property
    def api(self) -> Optional[RestAPI]:
        """Return the api that is configured. If no api is available `None` is returned."""
        return self._api

    @property
    def engine(self) -> Engine:
        """Return the engine that is used to schedule and run the tasks."""
        return self._engine

    @property
    def tasks(self) -> TaskSet:
        """Return the tasks that are configured for this application."""
        return self._tasks

    @classmethod
    def from_file(cls, file_path: str) -> 'Application':
        """
        Loads the application from a configuration file.

        Args:
            file_path (str): Where the configuration file is located.
        """
        config = load_config(str(file_path))
        PayloadSelector.instance.register_udfs(config.udfs)  # pylint: disable=no-member
        app = Application(config)
        return app
