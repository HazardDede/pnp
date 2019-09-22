"""The actual application wrapper around tasks and engine."""

import os
from typing import Optional

from .config import load_config
from .engines import Engine, DEFAULT_ENGINES
from .models import TaskSet, TaskModel, UDFModel, tasks_to_str
from .selector import PayloadSelector
from .shared.exc import NoEngineError
from .utils import Loggable
from .validator import Validator


class Application(Loggable):
    """The wrapper that knows about tasks and engine."""
    def __init__(self, tasks: TaskSet):
        self._tasks = tasks
        self._engine = None  # type: Optional[Engine]

    def start(self) -> None:
        """Starts the application."""
        if not self._engine:
            raise NoEngineError()
        self._engine.run(self._tasks)

    def bind(self, engine: Engine) -> None:
        """Binds an engine to the application."""
        Validator.is_instance(Engine, engine=engine)
        self._engine = engine

    @classmethod
    def from_file(cls, file_path: str, engine_override: Optional[str] = None) -> 'Application':
        """
        Loads the application from a configuration file.

        Args:
            file_path (str): Where the configuration file is located.
            engine_override (str): If given overwrites the engine that is specified inside the
                configuration file.
        """
        Validator.one_of(list(DEFAULT_ENGINES.keys()), allow_none=True,
                         engine_override=engine_override)

        udfs, engine, task_cfg = load_config(file_path)
        base_path = os.path.dirname(file_path)
        tasks = {
            task.name: TaskModel.from_dict(task, base_path) for task in task_cfg
        }
        if engine_override:
            engine = DEFAULT_ENGINES[engine_override]()
        elif engine is None:
            # Backward compatibility
            engine = DEFAULT_ENGINES['thread']()
        if udfs is not None:
            udfs = [UDFModel.from_config(udf) for udf in udfs]
            PayloadSelector.instance.register_udfs(udfs)  # pylint: disable=no-member

        from pprint import pformat
        # pylint: disable=no-member
        cls.logger.info("UDFs\n{}".format(pformat(udfs)))
        cls.logger.info("Engine\n{}".format(engine))
        cls.logger.info("Configured tasks\n{}".format(tasks_to_str(tasks)))
        # pylint: enable=no-member
        app = Application(tasks=tasks)
        app.bind(engine=engine)
        return app
