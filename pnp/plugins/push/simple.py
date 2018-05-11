from . import PushBase


class Echo(PushBase):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def push(self, payload):
        self.logger.info("[{self.name}] Got {payload}".format(**locals()))
