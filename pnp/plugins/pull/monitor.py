"""Monitoring related plugins."""

import os
import subprocess

import psutil

from pnp.plugins.pull import Polling


class Stats(Polling):
    """
    Periodically emits stats about the host system, like cpu_use, memory_use, swap_use, ...

    See Also:
        https://github.com/HazardDede/pnp/blob/master/docs/plugins/pull/monitor.Stats/index.md
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
            with open('/sys/class/thermal/thermal_zone0/temp') as tzone:
                return round(float(tzone.read()) * 0.001, 1)
        except FileNotFoundError:  # pragma: no cover
            return 0.0

    @staticmethod
    def _cpu_freq():
        freq = psutil.cpu_freq()
        if not freq:
            return 0
        return freq.current

    @staticmethod
    def _throttled():
        # Raspberry only
        try:
            mask1 = 1  # under voltage
            mask2 = 2  # arm frequency capped
            mask4 = 4  # throttled
            mask8 = 8  # soft temperature limit throttle (pi3 b+)

            out = subprocess.run(
                ['vcgencmd', 'get_throttled'],
                stdout=subprocess.PIPE,
                check=False
            ).stdout.decode('utf-8')
            hex_num = int(out[out.find('=') + 1:], 16)

            return (
                int(bool(hex_num & mask1)),
                int(bool(hex_num & mask2)),
                int(bool(hex_num & mask4)),
                int(bool(hex_num & mask8)),
            )
        except FileNotFoundError:
            return 0, 0, 0, 0

    def poll(self):
        l1m, l5m, l15m = os.getloadavg()
        uvolt, fcap, throttled, temp_limit = self._throttled()
        return {
            'cpu_count': psutil.cpu_count(),
            'cpu_freq': self._cpu_freq(),
            'cpu_temp': self._cpu_temp(),
            'cpu_use': psutil.cpu_percent(),
            'disk_use': self._disk_usage(),
            'load_1m': l1m,
            'load_5m': l5m,
            'load_15m': l15m,
            'memory_use': psutil.virtual_memory().percent,
            'rpi_cpu_freq_capped': fcap,
            'rpi_temp_limit_throttle': temp_limit,
            'rpi_throttle': throttled,
            'rpi_under_voltage': uvolt,
            'swap_use': psutil.swap_memory().percent
        }
