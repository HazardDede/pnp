import pytest
from mock import patch

from pnp.mocking import FritzBoxHostsMock
from pnp.plugins.pull.presence import FritzBoxTracker


def _package_installed():
    try:
        import fritzconnection
        return True
    except ImportError:
        return False


@pytest.mark.skipif(not _package_installed(), reason="requires package fritzconnection")
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
        assert fritzmock.address == dut.CONF_DEFAULT_IP
        assert fritzmock.user == dut.CONF_DEFAULT_USER
        assert fritzmock.password == dut.CONF_DEFAULT_PASSWORD


@pytest.mark.skipif(not _package_installed(), reason="requires package fritzconnection")
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


@pytest.mark.skipif(not _package_installed(), reason="requires package fritzconnection")
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


@pytest.mark.skipif(not _package_installed(), reason="requires package fritzconnection")
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
