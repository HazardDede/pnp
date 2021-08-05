import os
import time
from ftplib import FTP
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pytest

from pnp.plugins.pull.net import ftpserver as ftp
from tests.plugins.pull import make_runner, start_runner


def path_to_test_file():
    return os.path.join(os.path.dirname(__file__), '../../../resources/faces/obama.jpg')


def test_init_default():
    dut = ftp.FTPServer(name='pytest')
    assert dut.events == ftp.ALL_EVENTS
    assert dut.port == 2121
    assert dut.user is None
    assert dut.max_cons == 256
    assert dut.max_cons_ip == 5


def test_init_user_pwd():
    dut = ftp.FTPServer(name='pytest', user_pwd=None)
    assert dut.user is None
    assert dut.password is None

    dut = ftp.FTPServer(name='pytest', user_pwd='admin')
    assert dut.user == 'admin'
    assert dut.password == ''

    dut = ftp.FTPServer(name='pytest', user_pwd=('admin', 'root'))
    assert dut.user == 'admin'
    assert dut.password == 'root'


def test_init_events():
    dut = ftp.FTPServer(name='pytest', events='login')
    assert dut.events == [ftp.EVENT_LOGIN]

    dut = ftp.FTPServer(name='pytest', events=('login', 'logout'))
    assert dut.events == [ftp.EVENT_LOGIN, ftp.EVENT_LOGOUT]

    with pytest.raises(ValueError, match="Argument 'events' is expected to be a subset of") as err:
        ftp.FTPServer(name='pytest', events='unknown')


@pytest.mark.asyncio
async def test_pull_connect_login_disconnect():
    dut = ftp.FTPServer(name='pytest')

    runner = await make_runner(dut)
    async with start_runner(runner):
        time.sleep(0.5)
        client = FTP()
        client.connect('localhost', 2121)
        client.login()
        client.close()
        time.sleep(0.2)

    assert runner.events == [
        {'event': 'connect', 'data': {}},
        {'event': 'login', 'data': {'user': 'anonymous'}},
        {'event': 'disconnect', 'data': {}},
    ]


@pytest.mark.asyncio
async def test_pull_connect_login_user_disconnect():
    dut = ftp.FTPServer(name='pytest', user_pwd=('root', 'admin'))

    runner = await make_runner(dut)
    async with start_runner(runner):
        time.sleep(0.5)
        client = FTP()
        client.connect('localhost', 2121)
        client.login(user='root', passwd='admin')
        client.close()
        time.sleep(0.2)

    assert runner.events == [
        {'event': 'connect', 'data': {}},
        {'event': 'login', 'data': {'user': 'root'}},
        {'event': 'disconnect', 'data': {}},
    ]


@pytest.mark.asyncio
async def test_pull_connect_store_retr_disconnect():
    with TemporaryDirectory() as tmpdir:
        dut = ftp.FTPServer(name='pytest', directory=tmpdir)

        runner = await make_runner(dut)
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

        assert runner.events == [
            {'event': 'connect', 'data': {}},
            {'event': 'login', 'data': {'user': 'anonymous'}},
            {'event': 'file_received', 'data': {'file_path': os.path.join(os.path.realpath(tmpdir), 'test.txt')}},
            {'event': 'file_sent', 'data': {'file_path': os.path.join(os.path.realpath(tmpdir), 'test.txt')}},
            {'event': 'disconnect', 'data': {}},
        ]


def test_repr():
    dut = ftp.FTPServer(name='pytest')
    assert repr(dut) == (
        "FTPServer(directory=None, events=['connect', 'disconnect', 'file_received', 'file_received_incomplete', "
        "'file_sent', 'file_sent_incomplete', 'login', 'logout'], max_cons=256, max_cons_ip=5, name='pytest', "
        "password=None, port=2121, user=None)"
    )


def test_backwards_compat():
    from pnp.plugins.pull.ftp import Server
