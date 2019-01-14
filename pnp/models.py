from typing import Dict, List, Optional, Union

import attr
from box import Box

from .plugins import load_plugin
from .plugins.pull import PullBase
from .plugins.push import PushBase
from .plugins.udf import UserDefinedFunction

TaskName = str
TaskCfg = Union[Box, dict]
UDFCfg = Union[Box, dict]


def _validate_deps(instance, attrib, val):
    if val is None:
        return None
    if not isinstance(val, list):
        raise TypeError("Dependencies is expected to be a list of pushes")
    for exp_push in val:
        if not isinstance(exp_push, PushModel):
            raise TypeError("A dependency is expected to be a child of pnp.plugins.push.PushBase")


def _validate_pushes(instance, attrib, val):
    if not isinstance(val, list):
        raise TypeError("Pushes is expected to be a list of pushes")
    for exp_push in val:
        if not isinstance(exp_push, PushModel):
            raise TypeError("A push is expected to be a child of pnp.models.Push")


def _validate_callable(instance, attrib, val):
    if not callable(val):
        raise TypeError("The value is expected to be a callable")


@attr.s
class PullModel:
    instance = attr.ib(validator=attr.validators.instance_of(PullBase))


@attr.s
class PushModel:
    instance = attr.ib(validator=attr.validators.instance_of(PushBase))
    selector = attr.ib(validator=attr.validators.optional(attr.validators.instance_of((str, list, dict))), default=None)
    unwrap = attr.ib(converter=bool, default=False)
    deps = attr.ib(validator=_validate_deps, default=list())


@attr.s
class TaskModel:
    name = attr.ib(converter=str)
    pull = attr.ib(validator=attr.validators.instance_of(PullModel))
    pushes = attr.ib(validator=_validate_pushes)

    @classmethod
    def mk_pull(cls, task: TaskCfg, **extra) -> PullModel:
        args = {'name': '{task.name}_pull'.format(task=task), **extra, **task.pull.args}
        return PullModel(instance=load_plugin(task.pull.plugin, PullBase, **args))

    @classmethod
    def mk_push(cls, task: TaskCfg, **extra) -> List[PushModel]:
        def _many(pushlist, prefix):
            for i, push in enumerate(pushlist):
                push_name = '{prefix}_{i}'.format(**locals())
                args = {'name': push_name, **extra, **push.args}
                unwrap = getattr(push, 'unwrap', False)
                yield PushModel(
                    instance=load_plugin(push.plugin, PushBase, **args),
                    selector=push.selector,
                    unwrap=unwrap,
                    deps=list(_many(push.deps, push_name))
                )
        return list(_many(task.pushes, "{task.name}_push".format(**locals())))

    @classmethod
    def from_dict(cls, task: TaskCfg, base_path: Optional[str] = None) -> 'TaskModel':
        if not isinstance(task, Box):
            task = Box(dict(base=task)).base

        extra = {'base_path': base_path}
        return cls(
            name=task.name,
            pull=cls.mk_pull(task, **extra),
            pushes=list(cls.mk_push(task, **extra))
        )


@attr.s
class UDFModel:
    name = attr.ib(converter=str)
    callable = attr.ib(validator=_validate_callable)

    @classmethod
    def from_config(cls, dct: UDFCfg) -> 'UDFModel':
        if not isinstance(dct, Box):
            dct = Box(dct)
        udf_type = 'callable' if not hasattr(dct, 'args') else UserDefinedFunction
        instantiate = hasattr(dct, 'args')
        kwargs = dict() if not hasattr(dct, 'args') or dct.args is None else dct.args
        fun = load_plugin(dct.plugin, udf_type, instantiate, **{'name': dct.name, **kwargs})
        return cls(name=dct.name, callable=fun)


TaskSet = Dict[str, TaskModel]


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
