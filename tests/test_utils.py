from .context import pnp


def test_loggable_smoke():
    class NeedsLogger(pnp.utils.Loggable):
        def do(self, message):
            self.logger.info(message)

    dut = NeedsLogger()
    dut.do("log me")
