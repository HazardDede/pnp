import time

from pnp.plugins.udf.simple import Counter, Memory


def test_throttle():
    dut = Counter(name='pytest', throttle="1s", init=0)
    assert dut() == 0
    assert dut() == 0  # Returns cached value
    assert dut() == 0  # Returns cached value
    time.sleep(1)
    assert dut() == 1  # 1s is over ...
    assert dut() == 1  # Returns cached value


def test_memory():
    dut = Memory(name='pytest')
    assert dut(1) == 1
    assert dut() == 1
    assert dut(2) == 1
    assert dut() == 2

    dut = Memory(name='pytest', init=1)
    assert dut(2) == 1
    assert dut(3) == 2
