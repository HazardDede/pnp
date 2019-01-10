from abc import abstractmethod

from .. import Plugin


class UserDefinedFunction(Plugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self, *args, **kwargs):
        return self.action(*args, **kwargs)

    @abstractmethod
    def action(self, *args, **kwargs):
        raise NotImplementedError()
