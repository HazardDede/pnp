from abc import abstractmethod

from .. import Plugin


class PushBase(Plugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @abstractmethod
    def push(self, payload):
        raise NotImplementedError()
