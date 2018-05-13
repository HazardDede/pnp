import logging
import os
import pprint
import sys
from collections import namedtuple

from .app import Application
from .config import load_config
from .plugins import load_plugin

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=LOG_LEVEL)


def mk_args(task, kind):
    if kind.lower() == 'inbound':
        return {'name': '{task.name}_inbound'.format(task=task), **task.inbound.args}
    return {'name': '{task.name}_outbound'.format(task=task), **task.outbound.args}


def tasks_to_str(tasks):
    res = []
    for _, t in tasks.items():
        res.append('{task.name} {{'.format(task=t))
        res.append('\tinbound = {task.inbound}'.format(task=t))
        res.append('\toutbound = {task.outbound}'.format(task=t))
        res.append('}')
    return "\n".join(res)


def main():
    cfg = load_config(sys.argv[1])
    Task = namedtuple("Task", ["name", "inbound", "outbound"])

    tasks = {
        task.name: Task(
            name=task.name,
            inbound=load_plugin(task.inbound.plugin, **mk_args(task, 'inbound')),
            outbound=load_plugin(task.outbound.plugin, **mk_args(task, 'outbound'))
        ) for task in cfg
    }

    logging.info("Configured tasks\n{}".format(tasks_to_str(tasks)))

    app = Application()
    app.run(tasks)


if __name__ == '__main__':
    main()
