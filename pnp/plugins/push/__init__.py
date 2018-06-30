import copy
from abc import abstractmethod

from .. import Plugin


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
