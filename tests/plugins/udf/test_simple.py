import time

from pnp.plugins.udf.simple import Counter


def test_throttle():
    dut = Counter(name='pytest', throttle="1s", init=0)
    assert dut() == 0
    assert dut() == 0  # Returns cached value
    assert dut() == 0  # Returns cached value
    time.sleep(1)
    assert dut() == 1  # 1s is over ...
    assert dut() == 1  # Returns cached value
