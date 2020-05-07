"""Data model."""

from typing import Dict, List, Optional, Union

import attr

from .plugins.pull import PullBase
from .plugins.push import PushBase
from .plugins.udf import UserDefinedFunction
from .typing import AnyCallable, SelectorExpression


def _validate_push_dependencies(instance, attrib, val):  # type: ignore
    _, _ = instance, attrib

    if val is None:
        return None
    if not isinstance(val, list):
        raise TypeError("Dependencies is expected to be a list of pushes")
    for exp_push in val:
        if not isinstance(exp_push, PushModel):
            raise TypeError("A dependency is expected to be a child of pnp.models.PushModel")
    return val


def _validate_pushes(instance, attrib, val):  # type: ignore
    _, _ = instance, attrib

    if not isinstance(val, list):
        raise TypeError("Pushes is expected to be a list of pushes")
    for exp_push in val:
        if not isinstance(exp_push, PushModel):
            raise TypeError("A push is expected to be a child of pnp.models.PushModel")


@attr.s
class PullModel:
    """Model representing a pull."""
    instance = attr.ib(
        validator=attr.validators.instance_of(PullBase)  # type: ignore
    )  # type: PullBase


@attr.s
class PushModel:
    """Model representing a push."""
    instance = attr.ib(
        validator=attr.validators.instance_of(PushBase)  # type: ignore
    )  # type: PushBase

    selector = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of((str, list, dict))),
        default=None
    )  # type: Optional[SelectorExpression]

    unwrap = attr.ib(
        converter=bool,
        default=False
    )  # type: bool

    deps = attr.ib(
        validator=_validate_push_dependencies,
        factory=list
    )  # type: List[PushModel]


@attr.s
class TaskModel:
    """Model representing a task (pull and dependant pushes)."""
    name = attr.ib(
        converter=str
    )  # type: str

    pull = attr.ib(
        validator=attr.validators.instance_of(PullModel)
    )  # type: PullModel

    pushes = attr.ib(
        validator=_validate_pushes
    )  # type: List[PushModel]


@attr.s
class UDFModel:
    """Model representing a user-defined function."""
    name = attr.ib(
        converter=str
    )  # type: str

    callable = attr.ib(
        validator=attr.validators.is_callable()
    )  # type: Union[AnyCallable, UserDefinedFunction]


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
