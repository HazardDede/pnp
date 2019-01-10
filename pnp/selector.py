from .models import UDFModel

from .utils import Singleton, safe_eval, FallbackBox, EvaluationError
from .validator import Validator


class PayloadSelector(Singleton):
    """
    Examples:

        >>> dut = PayloadSelector.instance

        >>> dut.eval_selector('payload.k1', dict(k1='k1', k2='k2'))
        'k1'
        >>> dut.eval_selector('suppress_me if int(payload) == 0 else int(payload)', 1)
        1
        >>> dut.eval_selector('suppress_me if int(payload) == 0 else int(payload)', 0) is dut.SuppressLiteral
        True
        >>> dut.eval_selector('on_off(data)', True)
        'on'

        >>> dut.instance.register_custom_global('on_off_custom', lambda x: 'on' if x else 'off')
        >>> dut.eval_selector('on_off_custom(data)', True)
        'on'
        >>> dut.eval_selector('on_off_custom(data)', False)
        'off'

        >>> payload = {'foo': {'bar': 1, 'baz': 2}}
        >>> dut.eval_selector({
        ...     "lambda payload: payload['foo']['bar']": 'baz',
        ...     "foo": "lambda payload: payload['foo']['baz']",
        ...     "lambda payload: payload['foo']['baz']": "lambda payload: payload['foo']['bar']"
        ... }, payload=payload) == {1: 'baz', 'foo': 2, 2: 1}
        True

        >>> dut.eval_selector([
        ...     "foo",
        ...     "lambda payload: payload['foo']['bar']",
        ...     "lambda payload: payload['foo']['baz']",
        ...     {"lambda payload: payload['foo']['bar']": "lambda payload: payload['foo']['baz']"},
        ...     ["foo", "bar", "lambda payload: payload['foo']['bar']"]
        ... ], payload=payload)
        ['foo', 1, 2, {1: 2}, ['foo', 'bar', 1]]

        >>> dut.eval_selector("payload", payload=payload) == {'foo': {'bar': 1, 'baz': 2}}
        True
        >>> dut.eval_selector({"payload": "payload"}, payload=payload)
        {'payload': 'payload'}
        >>> (dut.eval_selector({"payload": "lambda payload: payload"}, payload=payload)
        ...     == {'payload': {'foo': {'bar': 1, 'baz': 2}}})
        True

        >>> dut.eval_selector("this one is not known", payload=payload)
        Traceback (most recent call last):
        ...
        pnp.utils.EvaluationError: Failed to evaluate 'this one is not known'
        >>> dut.eval_selector(["lambda payload: known this is not"], payload=payload)
        Traceback (most recent call last):
        ...
        pnp.utils.EvaluationError: Your lambda is errorneous: 'lambda payload: known this is not'
        >>> dut.eval_selector(["lambda payload: known"], payload=payload)
        Traceback (most recent call last):
        ...
        pnp.utils.EvaluationError: Error when running the selector lambda: 'lambda payload: known'
        >>> dut.eval_selector({'str': 'str'}, payload=payload)  # Callables but no lambdas
        {'str': 'str'}
    """

    def __init__(self):
        self._suppress_literal = object()
        self._custom = {}
        self._register_globals()

    @property
    def SuppressLiteral(self):
        return self._suppress_literal

    @property
    def suppress_aliases(self):
        uppers = ["SUPPRESS", "SUPPRESSME", "SUPPRESSPUSH", "SUPPRESS_ME", "SUPPRESS_PUSH"]
        return uppers + [item.lower() for item in uppers]

    def _register_globals(self):
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
        import os
        self._custom["basename"] = os.path.basename
        from .utils import on_off
        self._custom["on_off"] = on_off

    def register_custom_global(self, name, fun):
        """
        Register a custom function that should be available in the context of the selector.

        Args:
            name: Name of the function to register.
            fun: The actual function to register.

        Returns:
            None.
        """
        Validator.is_function(fun=fun)
        Validator.is_instance(str, name=name)
        if name not in self._custom:  # Overriding a already existing custom will silently fail!
            self._custom[name] = fun

    def register_udfs(self, udfs):
        Validator.is_iterable_but_no_str(udfs=udfs)
        for i, udf in enumerate(udfs):
            Validator.is_instance(UDFModel, **{'udfs.item_{i}'.format(**locals()): udf})
            self.register_custom_global(udf.name, udf.callable)

    def _eval_wrapper(self, selector, payload):
        suppress_kwargs = {alias: self.SuppressLiteral for alias in self.suppress_aliases}
        return safe_eval(
            source=selector,
            payload=payload,
            data=payload,
            **suppress_kwargs,
            **self._custom
        )

    @staticmethod
    def _isalambda(v):
        LAMBDA = lambda: 0  # pylint: disable=E731
        return isinstance(v, type(LAMBDA)) and v.__name__ == LAMBDA.__name__

    def _e(self, snippet, payload, is_key=False):
        # There might be nested dicts or lists inside the complex structure... Eval them recursively
        if isinstance(snippet, dict):
            return {self._e(k, payload, True): self._e(v, payload) for k, v in snippet.items()}
        if isinstance(snippet, list):
            return [self._e(i, payload) for i in snippet]

        # Test if the snippet constructs a lambda -> assumes to be callable code with payload argument
        try:
            possible_fun = self._eval_wrapper(snippet, payload)
        except EvaluationError:
            if str(snippet).startswith('lambda'):
                raise EvaluationError("Your lambda is errorneous: '{snippet}'".format(**locals()))
            return snippet  # Evaluation failed -> assume that is string literal (dict key/value or list item)

        if not self._isalambda(possible_fun):
            return snippet  # Cannot be executed. So assume it is not a selector expression

        # It is a callable. Lets modify globals and call it :-)
        suppress_kwargs = {alias: self.SuppressLiteral for alias in self.suppress_aliases}
        customs = self._custom
        for k, v in {**suppress_kwargs, **customs}.items():
            possible_fun.__globals__[k] = v
        try:
            return possible_fun(payload)
        except:
            raise EvaluationError("Error when running the selector lambda: '{snippet}'".format(**locals()))

    def eval_selector(self, selector, payload):
        # Wrap payload inside a Box -> this makes dot accessable dictionaries possible
        # We create a dictionary cause payload might not be an actual dictionary.
        # This way wrapping with Box will always work ;-)
        payload = FallbackBox({'base': payload}).base
        if selector is None:
            return payload

        if isinstance(selector, (list, dict)):
            return self._e(selector, payload)  # Complex. Need additional magic

        # No complex structure. We assume that is an expression and we try to evaluate it
        return self._eval_wrapper(selector, payload)
