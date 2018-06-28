import copy
from abc import abstractmethod

from .. import Plugin
from ...utils import Singleton, safe_eval, FallbackBox


class PushBase(Plugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @abstractmethod
    def push(self, payload):
        raise NotImplementedError()  # pragma: no cover

    @staticmethod
    def envelope_payload(payload):
        """
        A payload might be enveloped (but actually it even may not). The actual payload will be available via
        data or payload inside the dictionary. All other keys are the envelope.
        Args:
            payload: Payload (which might be enveloped or not).

        Returns:
            A tuple consisting of envelope (might be None) and the real payload.

        Examples:

            >>> PushBase.envelope_payload(1234)  # No envelope -> payload as is
            ({}, 1234)
            >>> PushBase.envelope_payload({'key1': 'val1', 'key2': 'val2'}) == ({}, {'key1': 'val1', 'key2': 'val2'})
            True
            >>> PushBase.envelope_payload({'data': 1234})  # Envelope with the data key only
            ({}, 1234)
            >>> PushBase.envelope_payload({'payload': 1234})  # Works with 'payload' as well
            ({}, 1234)
            >>> PushBase.envelope_payload({'envelope1': 'envelope', 'payload': 1234})  # With actual envelope
            ({'envelope1': 'envelope'}, 1234)
        """
        payload = copy.deepcopy(payload)

        if not isinstance(payload, dict):
            return {}, payload

        if 'data' in payload:
            real_payload = payload.pop('data')
        elif 'payload' in payload:
            real_payload = payload.pop('payload')
        else:
            return {}, payload  # There is no envelope

        return payload, real_payload  # We popped the real payload -> all what is left in payload is the envelope


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
