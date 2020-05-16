import time

import pytest

import pnp.engines as eng


@pytest.mark.asyncio
async def test_simple_retry_handler():
    dut = eng.SimpleRetryHandler(retry_wait="1m")
    assert await dut.handle_error() == eng.RetryDirective(abort=False, wait_for=60, retry_cnt=1)
    dut = eng.SimpleRetryHandler(retry_wait=5)
    assert await dut.handle_error() == eng.RetryDirective(abort=False, wait_for=5, retry_cnt=1)

    dut = eng.SimpleRetryHandler(retry_wait=5)
    await dut.handle_error()
    res = await dut.handle_error()
    assert res == eng.RetryDirective(abort=False, wait_for=5, retry_cnt=2)


@pytest.mark.asyncio
async def test_limited_retry_handler_abort_when_max_retries_is_hit():
    dut = eng.LimitedRetryHandler(retry_wait="2m", max_retries=1)
    assert await dut.handle_error() == eng.RetryDirective(abort=False, wait_for=120, retry_cnt=1)
    assert await dut.handle_error() == eng.RetryDirective(abort=True, wait_for=120, retry_cnt=2)
    assert await dut.handle_error() == eng.RetryDirective(abort=True, wait_for=120, retry_cnt=3)


@pytest.mark.asyncio
async def test_advanced_retry_handler_abort_when_max_retries_is_hit():
    dut = eng.AdvancedRetryHandler(retry_wait="2m", max_retries=1)
    assert await dut.handle_error() == eng.RetryDirective(abort=False, wait_for=120, retry_cnt=1)
    assert await dut.handle_error() == eng.RetryDirective(abort=True, wait_for=120, retry_cnt=2)
    assert await dut.handle_error() == eng.RetryDirective(abort=True, wait_for=120, retry_cnt=3)


@pytest.mark.asyncio
async def test_advanced_retry_handler_reset_retry_counter():
    dut = eng.AdvancedRetryHandler(retry_wait="2m", max_retries=1, reset_retry_threshold=1)
    assert await dut.handle_error() == eng.RetryDirective(abort=False, wait_for=120, retry_cnt=1)
    time.sleep(1)
    assert await dut.handle_error() == eng.RetryDirective(abort=False, wait_for=120, retry_cnt=1)
    assert await dut.handle_error() == eng.RetryDirective(abort=True, wait_for=120, retry_cnt=2)


@pytest.mark.asyncio
async def test_advanced_retry_handler_infinite_retries():
    dut = eng.AdvancedRetryHandler(retry_wait="2m", max_retries=None, reset_retry_threshold=1)
    for i in range(100):
        assert await dut.handle_error() == eng.RetryDirective(abort=False, wait_for=120, retry_cnt=i + 1)
