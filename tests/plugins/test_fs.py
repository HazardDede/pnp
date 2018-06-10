import os
import tempfile
import time
from functools import partial

import pytest

from pnp.plugins.pull.fs import FileSystemWatcher
from tests.plugins.helper import make_runner, start_runner


def _required_packages_installed():
    try:
        import watchdog
        return True
    except ImportError:
        return False


def _touch(tmpdir, filename):
    # print(datetime.now(), "Touched")
    open(os.path.join(tmpdir, filename), 'w').close()


def _modify(tmpdir, filename, content):
    # print(datetime.now(), "Modified")
    with open(os.path.join(tmpdir, filename), 'w') as fs:
        fs.write(content)


def _delete(tmpdir, filename):
    # print(datetime.now(), "Deleted")
    os.remove(os.path.join(tmpdir, filename))


def _move(tmpdir, filename, newname):
    # print(datetime.now(), "Moved")
    os.rename(os.path.join(tmpdir, filename), os.path.join(tmpdir, newname))


def _helper_file_system_watcher(config, operations, expected):
    WAIT_SLEEP = 1
    events = []

    def callback(plugin, payload):
        events.append(payload)

    with tempfile.TemporaryDirectory() as tmpdir:
        dut = FileSystemWatcher(name='pytest', path=tmpdir, **config)

        runner = make_runner(dut, callback)
        with start_runner(runner):
            time.sleep(1)
            time.sleep(WAIT_SLEEP)

            for op in operations:
                op(tmpdir)
                time.sleep(WAIT_SLEEP)

            time.sleep(2)

    exp = expected(tmpdir)
    assert len(events) == len(exp)
    assert all([actual == expected for actual, expected in zip(events, exp)])


@pytest.mark.skipif(not _required_packages_installed(), reason="requires package watchdog")
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


@pytest.mark.skipif(not _required_packages_installed(), reason="requires package watchdog")
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


@pytest.mark.skipif(not _required_packages_installed(), reason="requires package watchdog")
def test_file_system_watcher_pull_with_deferred_modified_results_in_one_event():
    def expected(tmpdir):
        return [
            {'operation': 'created', 'is_directory': False, 'source': os.path.join(tmpdir, 'foo.txt'),
             'destination': None, 'file': {'file_name': 'foo.txt', 'content': '', 'mode': 'r', 'base64': False}},
            {'operation': 'modified', 'is_directory': False, 'source': os.path.join(tmpdir, 'foo.txt'),
             'destination': None, 'file': {'file_name': 'foo.txt', 'content': 'Last one', 'mode': 'r', 'base64': False}}
        ]

    def _multiple_modifications(tmpdir):
        _modify(tmpdir, filename='foo.txt', content="First one")
        time.sleep(1)
        _modify(tmpdir, filename='foo.txt', content="Second one")
        time.sleep(1)
        _modify(tmpdir, filename='foo.txt', content="Last one")

    _helper_file_system_watcher(
        config=dict(ignore_directories=True, load_file=True, defer_modified=1.5),
        operations=[
            partial(_touch, filename='foo.txt'),
            _multiple_modifications
        ],
        expected=expected
    )


@pytest.mark.skipif(not _required_packages_installed(), reason="requires package watchdog")
def test_file_system_watcher_pull_with_defer_modified_correct_sequence():
    def expected(tmpdir):
        return [
            {'operation': 'created', 'is_directory': False, 'source': os.path.join(tmpdir, 'foo.txt'),
             'destination': None, 'file': {'file_name': 'foo.txt', 'content': '', 'mode': 'r', 'base64': False}},
            {'operation': 'modified', 'is_directory': False, 'source': os.path.join(tmpdir, 'foo.txt'),
             'destination': None, 'file': {'file_name': 'foo.txt', 'content': 'Last one', 'mode': 'r', 'base64': False}},
            {'operation': 'deleted', 'is_directory': False, 'source': os.path.join(tmpdir, 'foo.txt'),
             'destination': None}
        ]

    def _multiple_modifications(tmpdir):
        _modify(tmpdir, filename='foo.txt', content="First one")
        time.sleep(1)
        _modify(tmpdir, filename='foo.txt', content="Second one")
        time.sleep(1)
        _modify(tmpdir, filename='foo.txt', content="Last one")

    _helper_file_system_watcher(
        config=dict(ignore_directories=True, load_file=True, defer_modified=1.5),
        operations=[
            partial(_touch, filename='foo.txt'),
            _multiple_modifications,
            partial(_delete, filename='foo.txt')
        ],
        expected=expected
    )

