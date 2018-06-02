import tempfile

import time

import os

from functools import partial

from pnp.plugins.pull.fs import FileSystemWatcher
from tests.plugins.helper import make_runner


def _touch(tmpdir, filename):
    open(os.path.join(tmpdir, filename), 'w').close()


def _modify(tmpdir, filename, content):
    with open(os.path.join(tmpdir, filename), 'w') as fs:
        fs.write(content)


def _delete(tmpdir, filename):
    os.remove(os.path.join(tmpdir, filename))


def _move(tmpdir, filename, newname):
    os.rename(os.path.join(tmpdir, filename), os.path.join(tmpdir, newname))


def _helper_file_system_watcher(config, operations, expected):
    WAIT_SLEEP=5
    events = []

    def callback(plugin, payload):
        events.append(payload)

    with tempfile.TemporaryDirectory() as tmpdir:
        dut = FileSystemWatcher(name='pytest', path=tmpdir, **config)

        runner = make_runner(dut, callback)
        runner.start()
        time.sleep(WAIT_SLEEP)

        for op in operations:
            op(tmpdir)
            time.sleep(WAIT_SLEEP)

        runner.stop()
        runner.join()
        runner.raise_on_error()

    exp = expected(tmpdir)
    assert len(events) == len(exp)
    assert all([actual == expected for actual, expected in zip(events, exp)])


def test_file_system_watcher_pull():
    def expected(tmpdir):
        return [
            {'operation': 'created', 'is_directory': False, 'source': os.path.join(tmpdir, 'foo.txt'),
             'destination': None},
            {'operation': 'modified', 'is_directory': False, 'source': os.path.join(tmpdir, 'foo.txt'),
             'destination': None},
            {'operation': 'moved', 'is_directory': False, 'source': os.path.join(tmpdir, 'foo.txt'),
             'destination': os.path.join(tmpdir, 'baz.txt')},
            {'operation': 'deleted', 'is_directory': False, 'source': os.path.join(tmpdir, 'baz.txt'),
             'destination': None}
        ]

    _helper_file_system_watcher(
        config=dict(ignore_directories=True),
        operations=[
            partial(_touch, filename='foo.txt'),
            partial(_modify, filename='foo.txt', content='Blub'),
            partial(_move, filename='foo.txt', newname='baz.txt'),
            partial(_delete, filename='baz.txt')
        ],
        expected=expected
    )


def test_file_system_watcher_pull_with_load_file():
    def expected(tmpdir):
        return [
            {'operation': 'created', 'is_directory': False, 'source': os.path.join(tmpdir, 'foo.txt'),
             'destination': None, 'file': {'file_name': 'foo.txt', 'content': '', 'mode': 'r', 'base64': False}},
            {'operation': 'modified', 'is_directory': False, 'source': os.path.join(tmpdir, 'foo.txt'),
             'destination': None, 'file': {'file_name': 'foo.txt', 'content': 'Blub', 'mode': 'r', 'base64': False}},
            {'operation': 'deleted', 'is_directory': False, 'source': os.path.join(tmpdir, 'foo.txt'),
             'destination': None}
        ]

    _helper_file_system_watcher(
        config=dict(ignore_directories=True, load_file=True),
        operations=[
            partial(_touch, filename='foo.txt'),
            partial(_modify, filename='foo.txt', content='Blub'),
            partial(_delete, filename='foo.txt')
        ],
        expected=expected
    )

