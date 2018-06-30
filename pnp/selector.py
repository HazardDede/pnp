from base64 import b64encode, b64decode

from .utils import Singleton, safe_eval, FallbackBox, on_off
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
        self._custom["b64encode"] = b64encode
        self._custom["b64decode"] = b64decode
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

    def eval_selector(self, selector, payload):
        # Wrap payload inside a Box -> this makes dot accessable dictionaries possible
        # We create a dictionary cause payload might not be an actual dictionary.
        # This way wrapping with Box will always work ;-)
        payload = FallbackBox({'base': payload}).base
        if selector is None:
            return payload

        suppress_kwargs = {alias: self.SuppressLiteral for alias in self.suppress_aliases}
        return safe_eval(
            source=selector,
            payload=payload,
            data=payload,
            **suppress_kwargs,
            **self._custom
        )
