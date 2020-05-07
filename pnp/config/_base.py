"""Contains base classes for config parsers."""

from typing import Optional, Iterable, Any

import attr

from pnp.engines import Engine
from pnp.models import TaskSet, UDFModel, TaskModel


def _validate_tasks(instance: 'Configuration', attrib: Any, val: Any) -> Any:
    _, _ = instance, attrib

    if not isinstance(val, dict):
        raise TypeError(
            "Argument 'tasks' is expected to be a dictionary, but is {}".format(type(val))
        )
    for i, (key, value) in enumerate(val.items()):
        if not isinstance(key, str):
            raise TypeError(
                "Key at {} position is expected to be a str, but is {}".format(i, type(value))
            )
        if not isinstance(value, TaskModel):
            raise TypeError(
                "Value at {} position is expected to be a TaskModel, but is {}".format(
                    i, type(value)
                )
            )
    return val


def _validate_udfs(instance: 'Configuration', attrib: Any, val: Any) -> Any:
    _, _ = instance, attrib

    if val is None:
        return val  # None is ok

    if not isinstance(val, (tuple, list)):
        raise TypeError(
            "Argument 'tasks' is expected to be an iterable, but is {}".format(type(val))
        )
    for i, item in enumerate(val):
        if not isinstance(item, UDFModel):
            raise TypeError(
                "Item value at {} position is expected to be a UDFModel, but is {}".format(
                    i, type(item)
                )
            )
    return val


@attr.s
class Configuration:
    """Represents a parsed and valid configuration."""
    tasks = attr.ib(
        validator=_validate_tasks
    )  # type: TaskSet

    engine = attr.ib(
        validator=attr.validators.instance_of((type(None), Engine)),
        default=None
    )  # type: Optional[Engine]

    udfs = attr.ib(
        validator=_validate_udfs,
        default=None
    )  # type: Optional[Iterable[UDFModel]]
