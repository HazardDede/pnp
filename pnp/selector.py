"""Utility classes for the building block 'selector'."""

from typing import List, Callable, Dict, Any, Iterable

from typeguard import typechecked

from pnp import validator
from pnp.models import UDFModel
from pnp.typing import SelectorExpression, Payload
from pnp.utils import Singleton, safe_eval, FallbackBox, EvaluationError


class PayloadSelector(Singleton):
    """
    The actual selector implementation.
    Knows about globals, the suppress literal, udfs and how to evaluate
    simple and complex selector expressions.
    """

    def __init__(self: 'PayloadSelector') -> None:  # pylint: disable=super-init-not-called
        self._suppress_literal = object()
        self._custom = {}  # type: Dict[str, Callable[..., Any]]
        self._register_globals()

    @property
    def suppress(self) -> object:
        """Return the suppress literal."""
        return self._suppress_literal

    @property
    def suppress_aliases(self) -> List[str]:
        """Returns available aliases for the suppress literal."""
        uppers = ["SUPPRESS", "SUPPRESSME", "SUPPRESSPUSH", "SUPPRESS_ME", "SUPPRESS_PUSH"]
        return uppers + [item.lower() for item in uppers]

    def _register_globals(self) -> None:
        self._custom["abs"] = abs
        self._custom["bool"] = bool
        self._custom["dict"] = dict
        self._custom["float"] = float
        self._custom["getattr"] = getattr
        self._custom["hasattr"] = hasattr
        self._custom["hash"] = hash
        self._custom["int"] = int
        self._custom["isinstance"] = isinstance
        self._custom["len"] = len
        self._custom["list"] = list
        self._custom["max"] = max
        self._custom["min"] = min
        self._custom["ord"] = ord
        self._custom["pow"] = pow
        self._custom["reversed"] = reversed
        self._custom["round"] = round
        self._custom["sorted"] = sorted
        self._custom["str"] = str
        self._custom["zip"] = zip

        from base64 import b64encode, b64decode
        self._custom["b64encode"] = b64encode
        self._custom["b64decode"] = b64decode
        from datetime import datetime
        self._custom["now"] = datetime.now
        self._custom["utcnow"] = datetime.utcnow
        import os
        self._custom["basename"] = os.path.basename

        from .utils import on_off
        self._custom["on_off"] = on_off

    @typechecked
    def register_custom_global(self, name: str, fun: Callable[..., Any]) -> None:
        """
        Register a custom function that should be available in the context of the selector.

        Args:
            name: Name of the function to register.
            fun: The actual function to register.

        Returns:
            None.
        """
        if name not in self._custom:  # Overriding a already existing custom will silently fail!
            self._custom[name] = fun

    def register_udfs(self, udfs: Iterable[UDFModel]) -> None:
        """Register the given user-definied function."""
        validator.all_items(UDFModel, udfs=udfs)
        for udf in udfs:
            self.register_custom_global(udf.name, udf.callable)

    def _eval_wrapper(self, selector: str, payload: Payload) -> Payload:
        suppress_kwargs = {alias: self.suppress for alias in self.suppress_aliases}
        return safe_eval(
            source=selector,
            payload=payload,
            data=payload,
            **suppress_kwargs,
            **self._custom
        )

    @staticmethod
    def _isalambda(v: Any) -> bool:
        lambda_ = lambda: 0
        return isinstance(v, type(lambda_)) and v.__name__ == lambda_.__name__

    def _e(self, snippet: SelectorExpression, payload: Payload) -> Payload:
        # There might be nested dicts or lists inside the complex structure... Eval them recursively
        if isinstance(snippet, dict):
            return {self._e(k, payload): self._e(v, payload) for k, v in snippet.items()}
        if isinstance(snippet, list):
            return [self._e(i, payload) for i in snippet]

        # Test if the snippet constructs a lambda
        # -> assumes to be callable code with payload argument
        try:
            possible_fun = self._eval_wrapper(str(snippet), payload)
        except EvaluationError as eve:
            if str(snippet).startswith('lambda'):
                raise EvaluationError("Your lambda is errorneous: '{snippet}'".format(
                    **locals())) from eve
            # Evaluation failed -> assume that is string literal (dict key/value or list item)
            return snippet

        if not self._isalambda(possible_fun):
            return snippet  # Cannot be executed. So assume it is not a selector expression

        # It is a callable. Lets modify globals and call it :-)
        suppress_kwargs = {alias: self.suppress for alias in self.suppress_aliases}
        customs = self._custom
        for k, v in {**suppress_kwargs, **customs}.items():
            possible_fun.__globals__[k] = v
        try:
            return possible_fun(payload)
        except Exception as exc:
            raise EvaluationError("Error when running the selector lambda: '{snippet}'".format(
                **locals())) from exc

    def eval_selector(self, selector: SelectorExpression, payload: Payload) -> Payload:
        """Applies the specified selector to the given payload."""
        # Wrap payload inside a Box -> this makes dot accessable dictionaries possible
        # We create a dictionary cause payload might not be an actual dictionary.
        # This way wrapping with Box will always work ;-)
        payload = FallbackBox({'base': payload}).base
        if selector is None:
            return payload

        if isinstance(selector, (list, dict)):
            return self._e(selector, payload)  # Complex. Need additional magic

        # No complex structure. We assume that is an expression and we try to evaluate it
        return self._eval_wrapper(str(selector), payload)
