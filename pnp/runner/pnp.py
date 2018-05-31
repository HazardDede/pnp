import logging
import os
import sys

from ..app import Application
from ..config import load_config
from ..models import Task, Pull, Push
from ..plugins import load_plugin

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=LOG_LEVEL)


def mk_inbound(task):
    args = {'name': '{task.name}_pull'.format(task=task), **task.pull.args}
    return Pull(instance=load_plugin(task.pull.plugin, **args))


def mk_pushes(pushes, push_prefix):
    for i, push in enumerate(pushes):
        push_name = '{push_prefix}_{i}'.format(**locals())
        args = {'name': push_name, **push.args}
        yield Push(
            instance=load_plugin(push.plugin, **args),
            selector=push.selector,
            deps=list(mk_pushes(push.deps, push_name))
        )


def mk_outbound(task):
    return list(mk_pushes(task.pushes, "{task.name}_push".format(**locals())))


def tasks_to_str(tasks):
    res = []
    for _, t in tasks.items():
        res.append('{task.name} {{'.format(task=t))
        res.append('\tpull = {task.pull}'.format(task=t))
        res.append('\tpushes = ['.format())
        for push in t.pushes:
            res.append('\t\t{push}'.format(push=push))
        res.append('\t]')
        res.append('}')
    return "\n".join(res)


def main():
    cfg = load_config(sys.argv[1])

    tasks = {
        task.name: Task(
            name=task.name,
            pull=mk_inbound(task),
            pushes=list(mk_outbound(task))
        ) for task in cfg
    }

    logging.info("Configured tasks\n{}".format(tasks_to_str(tasks)))

    app = Application()
    app.run(tasks)


if __name__ == '__main__':
    main()
