from .config import load_config
from .engines.general import Engine
from .models import TaskSet, Task, tasks_to_str
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
        cfg = load_config(file_path)
        tasks = {
            task.name: Task.from_dict(task) for task in cfg
        }
        cls.logger.info("Configured tasks\n{}".format(tasks_to_str(tasks)))

        return Application(tasks=tasks)
