from . import PushBase


class Echo(PushBase):
    """
    This push simply logs the `payload` via the `logging` module.

    Examples:

        >>> dut = Echo(name="echo_push")
        >>> dut.push("I will be logged")
        'I will be logged'
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def push(self, payload):
        self.logger.info("[{self.name}] Got {payload}".format(**locals()))
        return payload


class Nop(PushBase):
    """
    Executes no operation at all. A call to push(...) just returns the payload.
    This push is useful when you only need the power of the selector for dependent pushes.

    Examples:

        >>> dut = Nop(name="nop_push")
        >>> dut.push('I will be returned unaltered')
        'I will be returned unaltered'
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def push(self, payload):
        return payload
