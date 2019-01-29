import os
import psutil

from . import Polling


class Stats (Polling):
    """
    Periodically emits stats about the host system, like cpu_use, memory_use, swap_use, ...
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def _root_path():
        return os.path.abspath(os.sep)

    @classmethod
    def _disk_usage(cls):
        try:
            return psutil.disk_usage(cls._root_path()).percent
        except FileNotFoundError:  # pragma: no cover
            return 0.0

    @staticmethod
    def _cpu_temp():
        try:
            # Raspberry
            with open('/sys/class/thermal/thermal_zone0/temp') as tz:
                return round(float(tz.read()) * 0.001, 1)
        except FileNotFoundError:  # pragma: no cover
            return 0.0

    @staticmethod
    def _cpu_freq():
        freq = psutil.cpu_freq()
        if not freq:
            return 0
        return freq.current

    def poll(self):
        l1m, l5m, l15m = os.getloadavg()
        return {
            'cpu_count': psutil.cpu_count(),
            'cpu_freq': self._cpu_freq(),
            'cpu_use': psutil.cpu_percent(),
            'cpu_temp': self._cpu_temp(),
            'memory_use': psutil.virtual_memory().percent,
            'swap_use': psutil.swap_memory().percent,
            'disk_use': self._disk_usage(),
            'load_1m': l1m,
            'load_5m': l5m,
            'load_15m': l15m
        }
