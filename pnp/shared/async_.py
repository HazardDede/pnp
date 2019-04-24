"""Asyncio helper."""

from concurrent.futures import Future
from typing import Callable, Any, Coroutine

import asyncio

from ..utils import StopCycleError
from ..validator import Validator


def async_from_sync(fun: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Calls an async function from a synchronous context."""

    async def _wrap(call_result: Any) -> None:
        """
        Wraps the awaitable with something that puts the result into the
        result/exception future.
        """
        try:
            result = await fun(*args, **kwargs)
        except Exception as exc:  # pylint: disable=broad-except
            call_result.set_exception(exc)
        else:
            call_result.set_result(result)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    call_result = Future()  # type: Any
    try:
        loop.run_until_complete(_wrap(call_result))
    finally:
        try:
            if hasattr(loop, "shutdown_asyncgens"):
                loop.run_until_complete(loop.shutdown_asyncgens())  # type: ignore
        finally:
            loop.close()

    return call_result.result()


async def async_interruptible_sleep(wait: float,
                                    callback: Callable[[], Coroutine[Any, Any, None]],
                                    interval: float = 0.5) -> None:
    """
    Waits the specified amount of time. The waiting can be interrupted when the callback raises a
    `StopCycleError`. The argument `interval` defines after how much waiting time the callback
    should be called to determine if the sleep should be interrupted or not.
    """
    wait = float(wait)
    interval = float(interval)

    complete_cycles = int(wait // interval)
    try:
        for _ in range(0, complete_cycles):
            await callback()  # Should raise a StopCycleError error when waiting should be aborted
            await asyncio.sleep(interval)

        await asyncio.sleep(wait % interval)
    except StopCycleError:
        pass


async def async_sleep_until_interrupt(sleep_time: float,
                                      interrupt_fun: Callable[[], Coroutine[Any, Any, bool]],
                                      interval: float = 0.5) -> None:
    """Call this method to sleep an interruptable sleep until the interrupt coroutine returns
    True."""
    Validator.is_function(interrupt_fun=interrupt_fun)

    async def callback() -> None:
        if await interrupt_fun():
            raise StopCycleError()
    await async_interruptible_sleep(sleep_time, callback, interval=interval)
