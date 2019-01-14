import os

from .config import load_config
from .engines import Engine, AdvancedRetryHandler
from .engines.thread import ThreadEngine
from .models import TaskSet, TaskModel, UDFModel, tasks_to_str
from .selector import PayloadSelector
from .utils import Loggable
from .validator import Validator


class Application(Loggable):
    def __init__(self, tasks: TaskSet):
        self._tasks = tasks
        self._engine = None

    def start(self):
        self._engine.run(self._tasks)

    def bind(self, engine: Engine):
        Validator.is_instance(Engine, engine=engine)
        self._engine = engine

    @classmethod
    def from_file(cls, file_path: str):
        udfs, engine, task_cfg = load_config(file_path)
        base_path = os.path.dirname(file_path)
        tasks = {
            task.name: TaskModel.from_dict(task, base_path) for task in task_cfg
        }
        if engine is None:
            # Backward compatibility
            engine = ThreadEngine(queue_worker=3, retry_handler=AdvancedRetryHandler())
        if udfs is not None:
            udfs = [UDFModel.from_config(udf) for udf in udfs]
            PayloadSelector.instance.register_udfs(udfs)

        from pprint import pformat
        cls.logger.info("UDFs\n{}".format(pformat(udfs)))
        cls.logger.info("Engine\n{}".format(engine))
        cls.logger.info("Configured tasks\n{}".format(tasks_to_str(tasks)))
        app = Application(tasks=tasks)
        app.bind(engine=engine)
        return app
