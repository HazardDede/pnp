from abc import abstractmethod
from datetime import datetime, timedelta

from .. import Plugin
from ...utils import parse_duration_literal


class UserDefinedFunction(Plugin):
    def __init__(self, throttle=None, **kwargs):
        super().__init__(**kwargs)
        self.throttle = throttle and parse_duration_literal(throttle)
        self._cache = None
        self._last_call = None

    def __call__(self, *args, **kwargs):
        if not self.throttle:
            return self.action(*args, **kwargs)

        # Invariant: self.throttle is not None
        n = datetime.now()
        if self._last_call is None:
            res = self.action(*args, **kwargs)
            self._cache = res
            self._last_call = n
            return res

        # Invariant: self._last_call is not None
        span = n - self._last_call
        if span >= timedelta(seconds=self.throttle):
            res = self.action(*args, **kwargs)
            self._cache = res
            self._last_call = n
            return res

        # Invariant: span < delta(throttle)
        return self._cache

    @abstractmethod
    def action(self, *args, **kwargs):
        raise NotImplementedError()
