"""Asyncio helper."""

import asyncio
from typing import Callable, Any, Coroutine

from pnp import validator
from pnp.typing import T
from pnp.utils import StopCycleError

SleepInterruptPredicate = Callable[[], Coroutine[Any, Any, bool]]
SleepInterruptCallback = Callable[[], Coroutine[Any, Any, None]]


async def async_interruptible_sleep(
    wait: float, callback: SleepInterruptCallback, interval: float = 0.1
) -> None:
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


async def async_sleep_until_interrupt(
    sleep_time: float, interrupt_fun: SleepInterruptPredicate, interval: float = 0.1
) -> None:
    """Call this method to sleep an interruptable sleep until the interrupt co-routine returns
    True."""
    validator.is_function(interrupt_fun=interrupt_fun)

    async def callback() -> None:
        if await interrupt_fun():
            raise StopCycleError()
    await async_interruptible_sleep(sleep_time, callback, interval=interval)


async def run_sync(func: Callable[..., T], *args: Any) -> T:
    """Runs sync code in an async compatible non-blocking way using an executor."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)
