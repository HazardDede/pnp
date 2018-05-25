from abc import abstractmethod

from .. import Plugin

SUPPRESS_PUSH = object()


class PushBase(Plugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @abstractmethod
    def push(self, payload):
        raise NotImplementedError()
