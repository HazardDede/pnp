import pytest
from mock import patch, MagicMock

from pnp.plugins.pull import PollingError
from pnp.plugins.pull.sensor import MiFlora


@pytest.yield_fixture()
def poller():
    with patch('btlewrap.BluepyBackend') as gatttool, patch('btlewrap.GatttoolBackend') as bluepy,\
            patch('miflora.miflora_poller.MiFloraPoller') as poller:
        gatttool.__name__ = 'gatttool mock'
        bluepy.__name__ = 'bluepy mock'

        def mock_return(param):
            res = {
                'conductivity': 800,
                'light': 2000,
                'moisture': 42,
                'battery': 72,
                'temperature': 24.2
            }
            return res[param]

        poller.return_value.parameter_value = MagicMock(side_effect=mock_return)
        poller.return_value.firmware_version.return_value = '1.0.0'
        yield poller


@pytest.mark.asyncio
async def test_poll_for_smoke(poller):
    dut = MiFlora(mac='C4:7C:8D:67:50:AB', name="pytest")
    res = await dut.poll()
    assert isinstance(res, dict)
    assert res.get('conductivity') == 800
    assert res.get('light') == 2000
    assert res.get('moisture') == 42
    assert res.get('battery') == 72
    assert res.get('temperature') == 24.2
    assert res.get('firmware') == '1.0.0'


@pytest.mark.asyncio
async def test_poll_backend_exception(poller):
    def raise_exc():
        raise IOError()
    poller.return_value.fill_cache = MagicMock(side_effect=raise_exc)

    dut = MiFlora(mac='C4:7C:8D:67:50:AB', name="pytest")
    with pytest.raises(PollingError):
        await dut.poll()

    def raise_exc():
        from btlewrap import BluetoothBackendException
        raise BluetoothBackendException()
    poller.return_value.fill_cache = MagicMock(side_effect=raise_exc)

    dut = MiFlora(mac='C4:7C:8D:67:50:AB', name="pytest")
    with pytest.raises(PollingError):
        dut._poll()


def test_repr():
    dut = MiFlora(mac='C4:7C:8D:67:50:AB', name="pytest")
    assert repr(dut) == "MiFlora(adapter='hci0', interval=60, is_cron=False, mac='C4:7C:8D:67:50:AB', name='pytest')"
