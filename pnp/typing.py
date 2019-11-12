"""Some typing stuff."""

from typing import Any, Dict, Union, List, Callable, Optional

from typing_extensions import Protocol

AnyCallable = Callable[..., Any]
DurationLiteral = Union[str, int, float]
Envelope = Dict[str, Any]
Payload = Any  # pylint: disable=invalid-name
SelectorExpression = Union[str, Dict[str, str], List[str]]


class QueuePutGet(Protocol):
    """Queue that supports put and get."""
    def get(self) -> Any:  # pylint: disable=unused-argument,missing-docstring,no-self-use
        ...

    def put(self, item: Any) -> None:  # pylint: disable=unused-argument,missing-docstring,no-self-use
        ...


class StopSignal(Protocol):
    """Stopping signal."""
    def set(self) -> None:  # pylint: disable=unused-argument,missing-docstring,no-self-use
        ...

    def is_set(self) -> bool:  # pylint: disable=unused-argument,missing-docstring,no-self-use
        ...


class ThreadLike(Protocol):
    """Thread like interface."""
    def is_alive(self) -> bool:  # pylint: disable=unused-argument,missing-docstring,no-self-use
        ...

    def join(self, timeout: Optional[float]) -> None:  # pylint: disable=unused-argument,missing-docstring,no-self-use
        ...

    def start(self) -> None:  # pylint: disable=unused-argument,missing-docstring,no-self-use
        ...
