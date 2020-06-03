"""Data model."""
from functools import partial
from typing import Dict, List, Optional, Union

import attr

from pnp.plugins.pull import PullBase
from pnp.plugins.push import PushBase
from pnp.plugins.udf import UserDefinedFunction
from pnp.typing import AnyCallable, SelectorExpression
from pnp.validator import attrs_validate_list_items


def _validate_push_dependencies(instance, attrib, val):  # type: ignore
    return attrs_validate_list_items(instance, attrib, val, item_type=PushModel)


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
        validator=attr.validators.instance_of((str, list, dict, type(None))),
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
        validator=partial(attrs_validate_list_items, item_type=PushModel)
    )  # type: List[PushModel]


@attr.s
class APIModel:
    """Model representing the api server configuration."""
    port = attr.ib(
        converter=int
    )  # type: int

    enable_swagger = attr.ib(
        converter=bool
    )  # type: bool

    enable_metrics = attr.ib(
        converter=bool
    )  # type: bool


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
