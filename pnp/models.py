from collections import namedtuple
from typing import Dict, List

from box import Box

from .plugins import load_plugin
from .plugins.pull import PullBase
from .plugins.push import PushBase

Task = namedtuple("Task", ["name", "pull", "pushes"])
Pull = namedtuple("Pull", ["instance"])
Push = namedtuple("Push", ["instance", "selector", "deps"])

TaskName = str
TaskCfg = Box
TaskSet = Dict[str, Task]


def _mk_pull(task: TaskCfg) -> Pull:
    args = {'name': '{task.name}_pull'.format(task=task), **task.pull.args}
    return Pull(instance=load_plugin(task.pull.plugin, PullBase, **args))


def _mk_push(task: TaskCfg) -> List[Push]:
    def _many(pushlist, prefix):
        for i, push in enumerate(pushlist):
            push_name = '{prefix}_{i}'.format(**locals())
            args = {'name': push_name, **push.args}
            yield Push(
                instance=load_plugin(push.plugin, PushBase, **args),
                selector=push.selector,
                deps=list(_many(push.deps, push_name))
            )
    return list(_many(task.pushes, "{task.name}_push".format(**locals())))


def from_dict(task: TaskCfg) -> Task:
    if not isinstance(task, Box):
        task = Box(dict(base=task)).base

    return Task(
        name=task.name,
        pull=_mk_pull(task),
        pushes=list(_mk_push(task))
    )


setattr(Task, 'from_dict', from_dict)


def tasks_to_str(tasks: TaskSet):
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
