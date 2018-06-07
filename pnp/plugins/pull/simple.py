import sys
import time

from . import PullBase


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
          plugin: pnp.plugins.pull.Count
          args:
            from_cnt: 0
            to_cnt: 10
            wait: 5
        push:
          plugin: pnp.plugins.push.Echo


    """

    def __init__(self, from_cnt=0, to_cnt=None, wait=5, **kwargs):
        super().__init__(**kwargs)
        self.from_cnt = int(from_cnt)
        self.to_cnt = int(to_cnt) if to_cnt is not None else None
        self.wait = float(wait)

    def pull(self):
        for i in range(self.from_cnt, self.to_cnt or sys.maxsize):
            self.notify(i)
            if self.stopped:
                break
            time.sleep(self.wait)


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
      plugin: pnp.plugins.pull.Repeat
      args:
        repeat: "Hello World"  # Repeats 'Hello World'
        wait: 1  # Every second
    push:
      plugin: pnp.plugins.push.Echo

    """

    def __init__(self, repeat, wait=5, **kwargs):
        super().__init__(**kwargs)
        self.repeat = repeat
        self.wait = float(wait)

    def pull(self):
        while not self.stopped:
            self.notify(self.repeat)
            time.sleep(self.wait)
