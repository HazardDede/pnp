import pytest
from mock import patch

from pnp.mocking import FritzBoxHostsMock
from pnp.plugins.pull.presence import SpecificFritzBoxTracker


def _package_installed():
    try:
        import fritzconnection
        return True
    except ImportError:
        return False


@pytest.mark.skipif(not _package_installed(), reason="requires package fritzconnection")
def test_polling():
    with patch('fritzconnection.lib.fritzhosts.FritzHosts', FritzBoxHostsMock()) as fritzmock:
        dut = SpecificFritzBoxTracker(name='pytest', whitelist=['12:34:56:78:12', '12:34:56:78:14'])
        assert dut.poll() == [
            {"mac": "12:34:56:78:12", 'ip': '192.168.178.10', 'name': 'pc1', 'status': True},
            {"mac": "12:34:56:78:14", 'ip': '192.168.178.12', 'name': 'pc3', 'status': True},
        ]
        assert dut.poll() == [
            {"mac": "12:34:56:78:12", 'ip': '192.168.178.10', 'name': 'pc1', 'status': True},
            {"mac": "12:34:56:78:14", 'ip': '192.168.178.12', 'name': 'pc3', 'status': False},
        ]


@pytest.mark.skipif(not _package_installed(), reason="requires package fritzconnection")
def test_polling_with_offline_delay():
    with patch('fritzconnection.lib.fritzhosts.FritzHosts', FritzBoxHostsMock()) as fritzmock:
        dut = SpecificFritzBoxTracker(
            name='pytest',
            whitelist=['12:34:56:78:12', '12:34:56:78:14'],
            offline_delay=1
        )
        assert dut.poll() == [
            {"mac": "12:34:56:78:12", 'ip': '192.168.178.10', 'name': 'pc1', 'status': True},
            {"mac": "12:34:56:78:14", 'ip': '192.168.178.12', 'name': 'pc3', 'status': True},
        ]
        assert dut.poll() == [
            {"mac": "12:34:56:78:12", 'ip': '192.168.178.10', 'name': 'pc1', 'status': True},
            {"mac": "12:34:56:78:14", 'ip': '192.168.178.12', 'name': 'pc3', 'status': True},
        ]
        assert dut.poll() == [
            {"mac": "12:34:56:78:12", 'ip': '192.168.178.10', 'name': 'pc1', 'status': True},
            {"mac": "12:34:56:78:14", 'ip': '192.168.178.12', 'name': 'pc3', 'status': False},
        ]
