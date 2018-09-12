import sys
import time

from . import PullBase, Polling
from ...validator import Validator


class Count(PullBase):
    """
    Emits every `wait` seconds a counting value which runs from `from_cnt` to `to_cnt`.
    If `to_cnt` is None will to count to infinity.

    Args:
        from_cnt (int): Where to start counting.
        to_cnt (int or None): Where to stop counting (if None will count to infinity).
        wait (float): Will wait that amount between counting emits.

    Returns:
        The `on_payload` callback will pass the current count as payload.

    Example configuration:

        name: count
        pull:
          plugin: pnp.plugins.pull.simple.Count
          args:
            from_cnt: 0
            to_cnt: 10
            wait: 5
        push:
          plugin: pnp.plugins.push.simple.Echo


    """

    def __init__(self, from_cnt=0, to_cnt=None, wait=5, **kwargs):
        super().__init__(**kwargs)
        self.from_cnt = int(from_cnt)
        self.to_cnt = int(to_cnt) if to_cnt is not None else None
        self.wait = float(wait)

    def pull(self):
        for i in range(self.from_cnt, self.to_cnt or sys.maxsize):
            self._sleep(self.wait)
            self.notify(i)
            if self.stopped:
                break


class Repeat(PullBase):
    """
    Emits every `wait` seconds the same `repeat`.

    Args:
        repeat (any): Will repeat this every emit.
        wait (float): Will wait that amount between counting emits.

    Returns:
        The `on_payload` callback will pass the repeated object as payload.

    Example configuration:

    name: repeat
    pull:
      plugin: pnp.plugins.pull.simple.Repeat
      args:
        repeat: "Hello World"  # Repeats 'Hello World'
        wait: 1  # Every second
    push:
      plugin: pnp.plugins.push.simple.Echo

    """

    def __init__(self, repeat, wait=5, **kwargs):
        super().__init__(**kwargs)
        self.repeat = repeat
        self.wait = float(wait)

    def pull(self):
        while not self.stopped:
            self._sleep(self.wait)
            self.notify(self.repeat)


class Infinite(PullBase):
    """Just for demonstration purposes. DO NOT USE!"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def pull(self):
        while True:
            try:
                time.sleep(0.5)
            except:
                pass


class CustomPolling(Polling):
    """
    Calls the specified callable every `interval`. The result of the callable is simply returned.

    Args:
        scheduled_callable (callable): Custom function to execute every `interval`.

    Returns:
        The `on_payload` callback will pass anything that the scheduled_callable has returned.

    Example configuration:

        Does not work with yaml or json configurations so far.
    """
    def __init__(self, scheduled_callable, **kwargs):
        super().__init__(**kwargs)
        self.scheduled_callable = scheduled_callable
        Validator.is_function(scheduled_callable=self.scheduled_callable)

    def poll(self):
        return self.scheduled_callable()
