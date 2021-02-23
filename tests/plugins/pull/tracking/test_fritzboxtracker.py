import pytest
from mock import patch

from pnp.plugins import BrokenImport
from pnp.plugins.pull.tracking import FritzBoxTracker
from tests.plugins.pull.tracking.mocking import FritzBoxHostsMock


def _plugin_available():
    from pnp.plugins.pull.tracking import FritzBoxTracker
    return not isinstance(FritzBoxTracker, BrokenImport)


@pytest.mark.skipif(not _plugin_available(), reason="requires package fritzconnection")
def test_polling():
    with patch('fritzconnection.lib.fritzhosts.FritzHosts', FritzBoxHostsMock()) as fritzmock:
        dut = FritzBoxTracker(name='pytest')
        assert dut._poll() == [
            {"mac": "12:34:56:78:12", 'ip': '192.168.178.10', 'name': 'pc1', 'status': True},
            {"mac": "12:34:56:78:13", 'ip': '192.168.178.11', 'name': 'pc2', 'status': False},
            {"mac": "12:34:56:78:14", 'ip': '192.168.178.12', 'name': 'pc3', 'status': True}
        ]
        assert dut._poll() == [
            {"mac": "12:34:56:78:12", 'ip': '192.168.178.10', 'name': 'pc1', 'status': True},
            {"mac": "12:34:56:78:13", 'ip': '192.168.178.11', 'name': 'pc2', 'status': False},
            {"mac": "12:34:56:78:14", 'ip': '192.168.178.12', 'name': 'pc3', 'status': False}
        ]
        assert fritzmock.address == '169.254.1.1'
        assert fritzmock.user == 'admin'
        assert fritzmock.password == ''


@pytest.mark.skipif(not _plugin_available(), reason="requires package fritzconnection")
def test_polling_with_offline_delay():
    with patch('fritzconnection.lib.fritzhosts.FritzHosts', FritzBoxHostsMock()):
        dut = FritzBoxTracker(name='pytest', offline_delay=2)
        assert dut._poll() == [
            {"mac": "12:34:56:78:12", 'ip': '192.168.178.10', 'name': 'pc1', 'status': True},
            {"mac": "12:34:56:78:13", 'ip': '192.168.178.11', 'name': 'pc2', 'status': False},
            {"mac": "12:34:56:78:14", 'ip': '192.168.178.12', 'name': 'pc3', 'status': True}
        ]
        assert dut._poll() == [
            {"mac": "12:34:56:78:12", 'ip': '192.168.178.10', 'name': 'pc1', 'status': True},
            {"mac": "12:34:56:78:13", 'ip': '192.168.178.11', 'name': 'pc2', 'status': False},
            {"mac": "12:34:56:78:14", 'ip': '192.168.178.12', 'name': 'pc3', 'status': True}
        ]
        assert dut._poll() == [
            {"mac": "12:34:56:78:12", 'ip': '192.168.178.10', 'name': 'pc1', 'status': True},
            {"mac": "12:34:56:78:13", 'ip': '192.168.178.11', 'name': 'pc2', 'status': False},
            {"mac": "12:34:56:78:14", 'ip': '192.168.178.12', 'name': 'pc3', 'status': True}
        ]
        assert dut._poll() == [
            {"mac": "12:34:56:78:12", 'ip': '192.168.178.10', 'name': 'pc1', 'status': True},
            {"mac": "12:34:56:78:13", 'ip': '192.168.178.11', 'name': 'pc2', 'status': False},
            {"mac": "12:34:56:78:14", 'ip': '192.168.178.12', 'name': 'pc3', 'status': False}
        ]


@pytest.mark.skipif(not _plugin_available(), reason="requires package fritzconnection")
def test_polling_whitelist():
    with patch('fritzconnection.lib.fritzhosts.FritzHosts', FritzBoxHostsMock()) as fritzmock:
        dut = FritzBoxTracker(name='pytest', whitelist=['12:34:56:78:12', '12:34:56:78:14'])
        assert dut._poll() == [
            {"mac": "12:34:56:78:12", 'ip': '192.168.178.10', 'name': 'pc1', 'status': True},
            {"mac": "12:34:56:78:14", 'ip': '192.168.178.12', 'name': 'pc3', 'status': True},
        ]
        assert dut._poll() == [
            {"mac": "12:34:56:78:12", 'ip': '192.168.178.10', 'name': 'pc1', 'status': True},
            {"mac": "12:34:56:78:14", 'ip': '192.168.178.12', 'name': 'pc3', 'status': False},
        ]


@pytest.mark.skipif(not _plugin_available(), reason="requires package fritzconnection")
def test_polling_whitelist_with_offline_delay():
    with patch('fritzconnection.lib.fritzhosts.FritzHosts', FritzBoxHostsMock()) as fritzmock:
        dut = FritzBoxTracker(
            name='pytest',
            whitelist=['12:34:56:78:12', '12:34:56:78:14'],
            offline_delay=1
        )
        assert dut._poll() == [
            {"mac": "12:34:56:78:12", 'ip': '192.168.178.10', 'name': 'pc1', 'status': True},
            {"mac": "12:34:56:78:14", 'ip': '192.168.178.12', 'name': 'pc3', 'status': True},
        ]
        assert dut._poll() == [
            {"mac": "12:34:56:78:12", 'ip': '192.168.178.10', 'name': 'pc1', 'status': True},
            {"mac": "12:34:56:78:14", 'ip': '192.168.178.12', 'name': 'pc3', 'status': True},
        ]
        assert dut._poll() == [
            {"mac": "12:34:56:78:12", 'ip': '192.168.178.10', 'name': 'pc1', 'status': True},
            {"mac": "12:34:56:78:14", 'ip': '192.168.178.12', 'name': 'pc3', 'status': False},
        ]


@pytest.mark.skipif(not _plugin_available(), reason="requires package fritzconnection")
def test_backwards_compat():
    from pnp.plugins.pull.presence import FritzBoxTracker
    _ = FritzBoxTracker
