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
        envelope, real_payload = self.envelope_payload(payload)
        self.logger.info("[{self.name}] Got '{real_payload}' with envelope '{envelope}'".format(**locals()))
        return payload  # Payload as is. With envelope (if any)


class Nop(PushBase):
    """
    Executes no operation at all. A call to push(...) just returns the payload.
    This push is useful when you only need the power of the selector for dependent pushes.

    Nop = No operation OR No push ;-)

    Examples:

        >>> dut = Nop(name="nop_push")
        >>> dut.push('I will be returned unaltered')
        'I will be returned unaltered'
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_payload = None

    def push(self, payload):
        self.last_payload = payload
        return payload
