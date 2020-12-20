"""Some typing stuff."""

from typing import Any, Dict, Union, List, Callable, Optional, TypeVar

# Generic Type T
T = TypeVar('T')

# Callable that allows any arguments and returns some value
AnyCallable = Callable[..., Any]

# Duration literal can be either something like 1h, 30 (for seconds) or 1.5 (seconds, but float)
DurationLiteral = Union[str, int, float]

# Metadata for the pull payload
Envelope = Dict[str, Any]

# Pull payload. Just for make things more readable
Payload = Any

# A valid expression for a selector is either
# * direct python code (str)
# * A dictionary with lambdas or literals (Dict[str, str])
# * A list of lambdas or literals
SelectorExpression = Optional[Union[str, Dict[Any, Any], List[Any]]]
