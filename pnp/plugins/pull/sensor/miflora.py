"""Pull: sensor.MiFlora"""
from typing import Any, Dict, Type, Optional

import miflora.miflora_poller as mfp
from btlewrap.base import AbstractBackend

from pnp.plugins.pull import PollingError, SyncPolling
from pnp.typing import Payload


__EXTRA__ = 'miflora'


class MiFlora(SyncPolling):
    """
    Periodically polls a xiaomi miflora plant sensor for sensor readings via btle.

    See Also:
        https://pnp.readthedocs.io/en/stable/plugins/index.html#sensor-miflora
    """
    __REPR_FIELDS__ = ['adapter', 'mac']

    def __init__(self, mac: str, adapter: str = 'hci0', **kwargs: Any):
        super().__init__(**kwargs)
        self.mac = str(mac)
        self.adapter = str(adapter)
        self._poller: Optional[mfp.MiFloraPoller] = None

    def _find_backend(self) -> Type[AbstractBackend]:
        try:
            import bluepy.btle  # noqa: F401 pylint: disable=unused-import
            from btlewrap import BluepyBackend
            backend = BluepyBackend
        except ImportError:
            from btlewrap import GatttoolBackend
            backend = GatttoolBackend
        self.logger.debug("Miflora for %s is using %s backend", self.mac, backend.__name__)
        return backend  # type: ignore

    def _init(self) -> None:
        if self._poller:
            # We already got a miflora poller -> abort
            return

        self._poller = mfp.MiFloraPoller(
            mac=self.mac, adapter=self.adapter, backend=self._find_backend()
        )
        self.logger.debug("Initialization for %s finished", self.mac)

    def _connect_sensor(self) -> None:
        assert self._poller

        from btlewrap import BluetoothBackendException
        try:
            self.logger.debug("Reading miflora sensor: %s", self.mac)
            self._poller.fill_cache()
        except (IOError, BluetoothBackendException) as err:
            raise PollingError() from err

    def _get_sensor_readings(self) -> Dict[str, Any]:
        assert self._poller

        reading_params = [mfp.MI_CONDUCTIVITY, mfp.MI_LIGHT, mfp.MI_MOISTURE,
                          mfp.MI_TEMPERATURE, mfp.MI_BATTERY]
        res = {para: self._poller.parameter_value(para) for para in reading_params}
        return {**res, **{'firmware': self._poller.firmware_version()}}

    def _poll(self) -> Payload:
        self._init()
        self._connect_sensor()
        readings = self._get_sensor_readings()
        self.logger.info("Miflora readings for '%s': %s", self.mac, readings)
        return readings
