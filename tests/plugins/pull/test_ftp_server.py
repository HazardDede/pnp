import os
import time
from ftplib import FTP
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pytest

import pnp.plugins.pull.ftp as ftp
from . import make_runner, start_runner


def path_to_test_file():
    return os.path.join(os.path.dirname(__file__), '../../resources/faces/obama.jpg')


def test_ftp_server_init_default():
    dut = ftp.Server(name='pytest')
    assert dut.events == ftp.Server.ALL_EVENTS
    assert dut.port == 2121
    assert dut.user is None
    assert dut.max_cons == 256
    assert dut.max_cons_ip == 5


def test_ftp_server_init_user_pwd():
    dut = ftp.Server(name='pytest', user_pwd=None)
    assert dut.user is None
    assert not hasattr(dut, 'password')

    dut = ftp.Server(name='pytest', user_pwd='admin')
    assert dut.user == 'admin'
    assert dut.password == ''

    dut = ftp.Server(name='pytest', user_pwd=('admin', 'root'))
    assert dut.user == 'admin'
    assert dut.password == 'root'

    with pytest.raises(TypeError, match=r"Argument 'user_pwd' is expected to be a str \(user\) or a tuple of user and password") as err:
        ftp.Server(name='pytest', user_pwd=5)


def test_ftp_server_init_events():
    dut = ftp.Server(name='pytest', events='login')
    assert dut.events == [dut.EVENT_LOGIN]

    dut = ftp.Server(name='pytest', events=('login', 'logout'))
    assert dut.events == [dut.EVENT_LOGIN, dut.EVENT_LOGOUT]

    with pytest.raises(ValueError, match="Argument 'events' is expected to be a subset of") as err:
        ftp.Server(name='pytest', events='unknown')


@pytest.mark.asyncio
async def test_ftp_server_pull_connect_login_disconnect():
    dut = ftp.Server(name='pytest')

    events = []
    def callback(plugin, payload):
        events.append(payload)

    runner = await make_runner(dut, callback)
    async with start_runner(runner):
        time.sleep(0.5)
        client = FTP()
        client.connect('localhost', 2121)
        client.login()
        client.close()
        time.sleep(0.2)

    assert events == [
        {'event': 'connect', 'data': {}},
        {'event': 'login', 'data': {'user': 'anonymous'}},
        {'event': 'disconnect', 'data': {}},
    ]


@pytest.mark.asyncio
async def test_ftp_server_pull_connect_login_user_disconnect():
    dut = ftp.Server(name='pytest', user_pwd=('root', 'admin'))

    events = []
    def callback(plugin, payload):
        events.append(payload)

    runner = await make_runner(dut, callback)
    async with start_runner(runner):
        time.sleep(0.5)
        client = FTP()
        client.connect('localhost', 2121)
        client.login(user='root', passwd='admin')
        client.close()
        time.sleep(0.2)

    assert events == [
        {'event': 'connect', 'data': {}},
        {'event': 'login', 'data': {'user': 'root'}},
        {'event': 'disconnect', 'data': {}},
    ]


@pytest.mark.asyncio
async def test_ftp_server_pull_connect_store_retr_disconnect():
    with TemporaryDirectory() as tmpdir:
        dut = ftp.Server(name='pytest', directory=tmpdir)

        events = []
        def callback(plugin, payload):
            events.append(payload)

        runner = await make_runner(dut, callback)
        async with start_runner(runner):
            time.sleep(0.5)
            client = FTP()
            client.connect('localhost', 2121)
            client.login()
            with open(path_to_test_file(), 'rb') as fread:
                client.storbinary('STOR test.txt', fread)
            with NamedTemporaryFile(delete=False) as temp:
                with open(temp.name, 'wb') as fwrite:
                    client.retrbinary('RETR test.txt', fwrite.write, 1024)
            client.close()
            time.sleep(0.2)

        assert events == [
            {'event': 'connect', 'data': {}},
            {'event': 'login', 'data': {'user': 'anonymous'}},
            {'event': 'file_received', 'data': {'file_path': os.path.join(os.path.realpath(tmpdir), 'test.txt')}},
            {'event': 'file_sent', 'data': {'file_path': os.path.join(os.path.realpath(tmpdir), 'test.txt')}},
            {'event': 'disconnect', 'data': {}},
        ]
