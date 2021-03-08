import os
import tempfile
import time
from functools import partial

import pytest

from pnp.plugins.pull.io import FSWatcher as FileSystemWatcher
from tests.plugins.pull import make_runner, start_runner


def _required_packages_installed():
    try:
        import watchdog
        return True
    except ImportError:
        return False


def _touch(tmpdir, filename):
    open(os.path.join(tmpdir, filename), 'w').close()


def _modify(tmpdir, filename, content):
    with open(os.path.join(tmpdir, filename), 'w') as fs:
        fs.write(content)


def _delete(tmpdir, filename):
    os.remove(os.path.join(tmpdir, filename))


def _move(tmpdir, filename, newname):
    os.rename(os.path.join(tmpdir, filename), os.path.join(tmpdir, newname))


async def _helper_file_system_watcher(config, operations, expected):
    WAIT_SLEEP = 0.5

    with tempfile.TemporaryDirectory() as tmpdir:
        dut = FileSystemWatcher(name='pytest', path=tmpdir, **config)

        runner = await make_runner(dut)
        async with start_runner(runner):
            time.sleep(1)
            time.sleep(WAIT_SLEEP)

            for op in operations:
                op(tmpdir)
                time.sleep(WAIT_SLEEP)

            # time.sleep(2)

    exp = expected(tmpdir)
    events = runner.events
    assert len(events) == len(exp)
    assert all([actual == expected for actual, expected in zip(events, exp)])


@pytest.mark.asyncio
@pytest.mark.skipif(not _required_packages_installed(), reason="requires package watchdog")
async def test_pull():
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

    await _helper_file_system_watcher(
        config=dict(ignore_directories=True),
        operations=[
            partial(_touch, filename='foo.txt'),
            partial(_modify, filename='foo.txt', content='Blub'),
            partial(_move, filename='foo.txt', newname='baz.txt'),
            partial(_delete, filename='baz.txt')
        ],
        expected=expected
    )


@pytest.mark.asyncio
@pytest.mark.skipif(not _required_packages_installed(), reason="requires package watchdog")
async def test_pull_with_load_file():
    def expected(tmpdir):
        return [
            {'operation': 'created', 'is_directory': False, 'source': os.path.join(tmpdir, 'foo.txt'),
             'destination': None, 'file': {'file_name': 'foo.txt', 'content': '', 'mode': 'r', 'base64': False}},
            {'operation': 'modified', 'is_directory': False, 'source': os.path.join(tmpdir, 'foo.txt'),
             'destination': None, 'file': {'file_name': 'foo.txt', 'content': 'Blub', 'mode': 'r', 'base64': False}},
            {'operation': 'deleted', 'is_directory': False, 'source': os.path.join(tmpdir, 'foo.txt'),
             'destination': None}
        ]

    await _helper_file_system_watcher(
        config=dict(ignore_directories=True, load_file=True),
        operations=[
            partial(_touch, filename='foo.txt'),
            partial(_modify, filename='foo.txt', content='Blub'),
            partial(_delete, filename='foo.txt')
        ],
        expected=expected
    )


@pytest.mark.asyncio
@pytest.mark.skipif(not _required_packages_installed(), reason="requires package watchdog")
async def test_pull_with_deferred_modified_results_in_one_event():
    def expected(tmpdir):
        return [
            {'operation': 'created', 'is_directory': False, 'source': os.path.join(tmpdir, 'foo.txt'),
             'destination': None, 'file': {'file_name': 'foo.txt', 'content': '', 'mode': 'r', 'base64': False}},
            {'operation': 'modified', 'is_directory': False, 'source': os.path.join(tmpdir, 'foo.txt'),
             'destination': None, 'file': {'file_name': 'foo.txt', 'content': 'Last one', 'mode': 'r', 'base64': False}}
        ]

    def _multiple_modifications(tmpdir):
        _modify(tmpdir, filename='foo.txt', content="First one")
        time.sleep(0.25)
        _modify(tmpdir, filename='foo.txt', content="Second one")
        time.sleep(0.25)
        _modify(tmpdir, filename='foo.txt', content="Last one")

    await _helper_file_system_watcher(
        config=dict(ignore_directories=True, load_file=True, defer_modified=0.5),
        operations=[
            partial(_touch, filename='foo.txt'),
            _multiple_modifications
        ],
        expected=expected
    )


@pytest.mark.asyncio
@pytest.mark.skipif(not _required_packages_installed(), reason="requires package watchdog")
async def test_pull_with_defer_modified_correct_sequence():
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
        time.sleep(0.25)
        _modify(tmpdir, filename='foo.txt', content="Second one")
        time.sleep(0.25)
        _modify(tmpdir, filename='foo.txt', content="Last one")

    await _helper_file_system_watcher(
        config=dict(ignore_directories=True, load_file=True, defer_modified=0.5),
        operations=[
            partial(_touch, filename='foo.txt'),
            _multiple_modifications,
            partial(_delete, filename='foo.txt')
        ],
        expected=expected
    )


def test_backwards_compat():
    from pnp.plugins.pull.fs import FileSystemWatcher
    _ = FileSystemWatcher


def test_repr():
    with tempfile.TemporaryDirectory() as tmpdir:
        dut = FileSystemWatcher(name='pytest', path=tmpdir)
        assert repr(dut) == (
            f"FSWatcher(base64=False, case_sensitive=False, defer_modified=0.5, events=None, ignore_directories=False, "
            f"ignore_patterns=None, load_file=False, mode='auto', name='pytest', "
            f"path='{tmpdir}', patterns=None, recursive=True)"
        )
