"""Pull: monitor.Stats."""

import os
import subprocess
from typing import Tuple

import psutil

from pnp.plugins.pull import SyncPolling
from pnp.typing import Payload

#
# CONSTANTS
#

CONST_CPU_COUNT = 'cpu_count'
CONST_CPU_FREQ = 'cpu_freq'
CONST_CPU_TEMP = 'cpu_temp'
CONST_CPU_USE = 'cpu_use'
CONST_DISK_USE = 'disk_use'
CONST_LOAD_1M = 'load_1m'
CONST_LOAD_5M = 'load_5m'
CONST_LOAD_15M = 'load_15m'
CONST_MEMORY_USE = 'memory_use'
CONST_RPI_FREQ_CAPPED = 'rpi_cpu_freq_capped'
CONST_RPI_TEMP_LIMIT_THROTTLE = 'rpi_temp_limit_throttle'
CONST_RPI_THROTTLE = 'rpi_throttle'
CONST_RPI_UNDER_VOLTAGE = 'rpi_under_voltage'
CONST_SWAP_USE = 'swap_use'


#
# Helper methods to collect statistics about the host system
#

def _root_path() -> str:
    return os.path.abspath(os.sep)


def _disk_usage() -> float:
    try:
        return psutil.disk_usage(_root_path()).percent  # type: ignore
    except FileNotFoundError:  # pragma: no cover
        return 0.0


def _cpu_temp() -> float:
    try:
        # Raspberry
        with open('/sys/class/thermal/thermal_zone0/temp') as tzone:
            return round(float(tzone.read()) * 0.001, 1)
    except FileNotFoundError:  # pragma: no cover
        return 0.0


def _cpu_freq() -> int:
    freq = psutil.cpu_freq()
    return freq.current if freq else 0  # type: ignore


def _rpi_throttled() -> Tuple[int, int, int, int]:
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


class Stats(SyncPolling):
    """
    Periodically emits stats about the host system, like cpu_use, memory_use, swap_use, ...

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#monitor-stats
    """

    def _poll(self) -> Payload:
        l1m, l5m, l15m = os.getloadavg()
        uvolt, fcap, throttled, temp_limit = _rpi_throttled()
        return {
            CONST_CPU_COUNT: psutil.cpu_count(),
            CONST_CPU_FREQ: _cpu_freq(),
            CONST_CPU_TEMP: _cpu_temp(),
            CONST_CPU_USE: psutil.cpu_percent(),
            CONST_DISK_USE: _disk_usage(),
            CONST_LOAD_1M: l1m,
            CONST_LOAD_5M: l5m,
            CONST_LOAD_15M: l15m,
            CONST_MEMORY_USE: psutil.virtual_memory().percent,
            CONST_RPI_FREQ_CAPPED: fcap,
            CONST_RPI_TEMP_LIMIT_THROTTLE: temp_limit,
            CONST_RPI_THROTTLE: throttled,
            CONST_RPI_UNDER_VOLTAGE: uvolt,
            CONST_SWAP_USE: psutil.swap_memory().percent
        }
