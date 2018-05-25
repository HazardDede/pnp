from . import PushBase


class Echo(PushBase):
    """
    Simply logs the payload.

    Examples:

        >>> dut = Echo(name="echo_push")
        >>> dut.push("I will be logged")
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def push(self, payload):
        self.logger.info("[{self.name}] Got {payload}".format(**locals()))
