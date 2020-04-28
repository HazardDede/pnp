import os
import tempfile
import time
from functools import partial

import pytest

from pnp.plugins.pull.camera import MotionEyeWatcher
from . import make_runner, start_runner


def _required_packages_installed():
    try:
        import watchdog
        return True
    except ImportError:
        return False


def _touch(tmpdir, dut, filename):
    # print(datetime.now(), "Touched")
    payload = {'operation': 'created', 'is_directory': False, 'source': os.path.join(tmpdir, filename),
               'destination': None}
    dut.notify(payload)


def _modify(tmpdir, dut, filename):
    payload = {'operation': 'modified', 'is_directory': False, 'source': os.path.join(tmpdir, filename),
               'destination': None}
    dut.notify(payload)


def _sleep(tmpdir, dut, secs=.5):
    time.sleep(secs)


def _do_operations(config, operations, expected):
    events = []

    def callback(plugin, payload):
        events.append(payload)

    with tempfile.TemporaryDirectory() as tmpdir:
        dut = MotionEyeWatcher(name='pytest', path=tmpdir, **config)

        runner = make_runner(dut, callback)
        with start_runner(runner):

            for op in operations:
                op(tmpdir, dut)

    exp = expected(tmpdir)
    assert len(events) == len(exp)
    assert all([actual == expected for actual, expected in zip(events, exp)])


@pytest.mark.skipif(not _required_packages_installed(), reason="requires package watchdog")
def test_motioneye_watcher():
    def expected(tmpdir):
        return [
            dict(event="motion", state="on"),
            dict(event="image", source=os.path.join(tmpdir, 'image.jpg')),
            dict(event="movie", source=os.path.join(tmpdir, 'movie.mp4')),
            dict(event="motion", state="off"),
            dict(event="motion", state="on"),
            dict(event="image", source=os.path.join(tmpdir, 'image2.jpg')),
            dict(event="image", source=os.path.join(tmpdir, 'image3.jpg')),
            dict(event="image", source=os.path.join(tmpdir, 'image4.jpg')),
            dict(event="image", source=os.path.join(tmpdir, 'image5.jpg')),
            dict(event="motion", state="off"),
        ]

    _do_operations(
        config=dict(motion_cool_down=1),
        operations=[
            partial(_touch, filename="image.jpg"),
            partial(_touch, filename="movie.mp4"),
            partial(_modify, filename="movie.mp4"),
            partial(_sleep, secs=1.2),
            partial(_touch, filename="image2.jpg"),
            partial(_touch, filename="image3.jpg"),
            partial(_touch, filename="image4.jpg"),
            partial(_touch, filename="image5.jpg"),
            partial(_sleep, secs=1.2)
        ],
        expected=expected
    )


@pytest.mark.skipif(not _required_packages_installed(), reason="requires package watchdog")
def test_motioneye_watcher_images_only():
    def expected(tmpdir):
        return [
            dict(event="motion", state="on"),
            dict(event="image", source=os.path.join(tmpdir, 'image.jpg')),
            dict(event="motion", state="off"),
            dict(event="motion", state="on"),
            dict(event="image", source=os.path.join(tmpdir, 'image2.jpg')),
            dict(event="image", source=os.path.join(tmpdir, 'image3.jpg')),
            dict(event="image", source=os.path.join(tmpdir, 'image4.jpg')),
            dict(event="image", source=os.path.join(tmpdir, 'image5.jpg')),
            dict(event="motion", state="off"),
        ]

    _do_operations(
        config=dict(motion_cool_down=1, movie_ext=None),
        operations=[
            partial(_touch, filename="image.jpg"),
            partial(_touch, filename="movie.mp4"),
            partial(_modify, filename="movie.mp4"),
            partial(_sleep, secs=1.2),
            partial(_touch, filename="image2.jpg"),
            partial(_touch, filename="image3.jpg"),
            partial(_touch, filename="image4.jpg"),
            partial(_touch, filename="image5.jpg"),
        ],
        expected=expected
    )


@pytest.mark.skipif(not _required_packages_installed(), reason="requires package watchdog")
def test_motioneye_watcher_movies_only():
    def expected(tmpdir):
        return [
            dict(event="motion", state="on"),
            dict(event="movie", source=os.path.join(tmpdir, 'movie.mp4')),
            dict(event="motion", state="off"),
        ]

    _do_operations(
        config=dict(motion_cool_down=1, image_ext=None),
        operations=[
            partial(_touch, filename="image.jpg"),
            partial(_touch, filename="movie.mp4"),
            partial(_modify, filename="movie.mp4"),
            partial(_sleep, secs=1.2),
            partial(_touch, filename="image2.jpg"),
            partial(_touch, filename="image3.jpg"),
            partial(_touch, filename="image4.jpg"),
            partial(_touch, filename="image5.jpg"),
        ],
        expected=expected
    )


@pytest.mark.skipif(not _required_packages_installed(), reason="requires package watchdog")
def test_motioneye_watcher_no_exts():
    with pytest.raises(TypeError, match="You have to specify either `image_file_ext`, `movie_file_ext` or both") as e:
        MotionEyeWatcher(name='pytest', path='/tmp', image_ext=None, movie_ext=None)
