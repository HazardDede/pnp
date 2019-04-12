"""Data model."""

from typing import Dict, List, Optional, Any, cast, Iterable, Union

import attr
from box import Box  # type: ignore

from .plugins import load_plugin
from .plugins.pull import PullBase
from .plugins.push import PushBase
from .plugins.udf import UserDefinedFunction
from .typing import AnyCallable, SelectorExpression


def _val_deps(instance, attrib, val):  # type: ignore  # pylint: disable=unused-argument
    if val is None:
        return None
    if not isinstance(val, list):
        raise TypeError("Dependencies is expected to be a list of pushes")
    for exp_push in val:
        if not isinstance(exp_push, PushModel):
            raise TypeError("A dependency is expected to be a child of pnp.plugins.push.PushBase")
    return val


def _val_pushes(instance, attrib, val):  # type: ignore  # pylint: disable=unused-argument
    if not isinstance(val, list):
        raise TypeError("Pushes is expected to be a list of pushes")
    for exp_push in val:
        if not isinstance(exp_push, PushModel):
            raise TypeError("A push is expected to be a child of pnp.models.Push")


def _val_callable(instance, attrib, val):  # type: ignore  # pylint: disable=unused-argument
    if not callable(val):
        raise TypeError("The value is expected to be a callable")


@attr.s
class PullModel:
    """Model representing a pull."""
    instance = attr.ib(validator=attr.validators.instance_of(PullBase))  # type: PullBase


@attr.s
class PushModel:
    """Model representing a push."""
    instance = attr.ib(validator=attr.validators.instance_of(PushBase))  # type: PushBase
    selector = attr.ib(validator=attr.validators.optional(
        attr.validators.instance_of((str, list, dict))  # type: ignore
    ), default=None)  # type: Optional[SelectorExpression]
    unwrap = attr.ib(converter=bool, default=False)  # type: bool
    deps = attr.ib(validator=_val_deps, default=list())  # type: List[PushModel]


@attr.s
class TaskModel:
    """Model representing a task (pull and dependant pushes)."""
    name = attr.ib(converter=str)  # type: str
    pull = attr.ib(validator=attr.validators.instance_of(PullModel))  # type: PullModel
    pushes = attr.ib(validator=_val_pushes)  # type: List[PushModel]

    @classmethod
    def mk_pull(cls, task: Box, **extra: Any) -> PullModel:
        """Make a pull out of a task configuration."""
        args = {'name': '{task.name}_pull'.format(task=task), **extra, **task.pull.args}
        return PullModel(instance=cast(PullBase, load_plugin(
            plugin_path=task.pull.plugin,
            plugin_type=PullBase,
            instantiate=True,
            **args
        )))

    @classmethod
    def mk_push(cls, task: Box, **extra: Any) -> List[PushModel]:
        """Make one or more pushes out of task configuration."""
        def _many(pushlist: List[Box], prefix: str) -> Iterable[PushModel]:
            for i, push in enumerate(pushlist):
                push_name = '{prefix}_{i}'.format(
                    i=i,
                    prefix=prefix
                )
                args = {'name': push_name, **extra, **push.args}
                unwrap = getattr(push, 'unwrap', False)
                yield PushModel(
                    instance=cast(PushBase, load_plugin(
                        plugin_path=push.plugin,
                        plugin_type=PushBase,
                        instantiate=True,
                        **args
                    )),
                    selector=push.selector,
                    unwrap=unwrap,
                    deps=list(_many(push.deps, push_name))
                )
        return list(_many(task.pushes, "{task.name}_push".format(**locals())))

    @classmethod
    def from_dict(cls, task: Box, base_path: Optional[str] = None) -> 'TaskModel':
        """Create a task from a task configuration."""
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
    """Model representing a user-defined function."""
    name = attr.ib(converter=str)  # type: str
    callable = attr.ib(validator=_val_callable)  # type: Union[AnyCallable, UserDefinedFunction]

    @classmethod
    def from_config(cls, dct: Union[Box, Dict[Any, Any]]) -> 'UDFModel':
        """Creates a UDFModel from a udf configuration snippet."""
        if not isinstance(dct, Box):
            dct = Box(dct)
        udf_type = cast(Union[str, type],
                        'callable' if not hasattr(dct, 'args') else UserDefinedFunction)
        instantiate = hasattr(dct, 'args')
        kwargs = dict() if not hasattr(dct, 'args') or dct.args is None else dct.args
        fun = load_plugin(
            plugin_path=dct.plugin,
            plugin_type=udf_type,
            instantiate=instantiate,
            **{'name': dct.name, **kwargs}
        )
        return cls(name=dct.name, callable=cast(UserDefinedFunction, fun))


TaskSet = Dict[str, TaskModel]


def tasks_to_str(tasks: TaskSet) -> str:
    """Transforms a set of tasks to a human readable representation."""
    res = []
    for _, task in tasks.items():
        res.append('{task.name} {{'.format(task=task))
        res.append('\tpull = {task.pull}'.format(task=task))
        res.append('\tpushes = ['.format())
        for push in task.pushes:
            res.append('\t\t{push}'.format(push=push))
        res.append('\t]')
        res.append('}')
    return "\n".join(res)
