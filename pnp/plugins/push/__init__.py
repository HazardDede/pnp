from abc import abstractmethod

from .. import Plugin
from ...utils import Singleton, safe_eval, FallbackBox


class PushBase(Plugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @abstractmethod
    def push(self, payload):
        raise NotImplementedError()  # pragma: no cover


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
    """

    def __init__(self):
        self._suppress_literal = object()

    @property
    def SuppressLiteral(self):
        return self._suppress_literal

    @property
    def suppress_aliases(self):
        uppers = ["SUPPRESS", "SUPPRESSME", "SUPPRESSPUSH", "SUPPRESS_ME", "SUPPRESS_PUSH"]
        return uppers + [item.lower() for item in uppers]

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
            **suppress_kwargs
        )
