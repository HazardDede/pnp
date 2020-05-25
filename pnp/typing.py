"""Some typing stuff."""

from typing import Any, Dict, Union, List, Callable, Optional

AnyCallable = Callable[..., Any]
DurationLiteral = Union[str, int, float]
Envelope = Dict[str, Any]
Payload = Any  # pylint: disable=invalid-name
SelectorExpression = Optional[Union[str, Dict[str, str], List[str]]]
