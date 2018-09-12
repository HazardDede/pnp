import time

import pnp.engines as eng


def test_simple_retry_handler():
    assert (eng.SimpleRetryHandler(retry_wait="1m").handle_error() ==
            eng.RetryDirective(abort=False, wait_for=60, retry_cnt=1))
    assert (eng.SimpleRetryHandler(retry_wait=5).handle_error() ==
            eng.RetryDirective(abort=False, wait_for=5, retry_cnt=1))

    dut = eng.SimpleRetryHandler(retry_wait=5)
    dut.handle_error()
    res = dut.handle_error()
    assert res == eng.RetryDirective(abort=False, wait_for=5, retry_cnt=2)


def test_limited_retry_handler_abort_when_max_retries_is_hit():
    dut = eng.LimitedRetryHandler(retry_wait="2m", max_retries=1)
    assert dut.handle_error() == eng.RetryDirective(abort=False, wait_for=120, retry_cnt=1)
    assert dut.handle_error() == eng.RetryDirective(abort=True, wait_for=120, retry_cnt=2)
    assert dut.handle_error() == eng.RetryDirective(abort=True, wait_for=120, retry_cnt=3)


def test_advanced_retry_handler_abort_when_max_retries_is_hit():
    dut = eng.AdvancedRetryHandler(retry_wait="2m", max_retries=1)
    assert dut.handle_error() == eng.RetryDirective(abort=False, wait_for=120, retry_cnt=1)
    assert dut.handle_error() == eng.RetryDirective(abort=True, wait_for=120, retry_cnt=2)
    assert dut.handle_error() == eng.RetryDirective(abort=True, wait_for=120, retry_cnt=3)


def test_advanced_retry_handler_reset_retry_counter():
    dut = eng.AdvancedRetryHandler(retry_wait="2m", max_retries=1, reset_retry_threshold=1)
    assert dut.handle_error() == eng.RetryDirective(abort=False, wait_for=120, retry_cnt=1)
    time.sleep(1)
    assert dut.handle_error() == eng.RetryDirective(abort=False, wait_for=120, retry_cnt=1)
    assert dut.handle_error() == eng.RetryDirective(abort=True, wait_for=120, retry_cnt=2)


def test_advanced_retry_handler_infinite_retries():
    dut = eng.AdvancedRetryHandler(retry_wait="2m", max_retries=None, reset_retry_threshold=1)
    for i in range(100):
        assert dut.handle_error() == eng.RetryDirective(abort=False, wait_for=120, retry_cnt=i + 1)
