import os
import time
import warnings

import pytest
from mock import patch

from pnp.mocking import PyAudioMock
from pnp.plugins.pull.sensor import Sound
from tests.conftest import resource_path
from . import start_runner, make_runner

ding_sound = os.path.join(resource_path('sounds'), 'ding.wav')
mock = PyAudioMock(ding_sound)


def _package_installed():
    try:
        import pyaudio
        import numpy
        import scipy
        return True
    except ImportError:
        return False


@pytest.mark.skipif(not _package_installed(), reason="requires package pyaudio, numpy, scipy")
@patch('pyaudio.PyAudio', mock)
def test_for_smoke_with_mode_pearson():
    config = [{Sound.CONF_PATH: ding_sound}]
    dut = Sound(name='pytest', wav_files=config, cool_down=0)

    events = []
    def callback(sender, payload):
        events.append(payload)

    runner = make_runner(dut, callback)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        with start_runner(runner):
            time.sleep(0.5)

    assert len(events) >= 1
    item = events[0]
    assert set(item.keys()) == {'data', 'threshold', 'corrcoef'}


@pytest.mark.skipif(not _package_installed(), reason="requires package pyaudio, numpy, scipy")
@patch('pyaudio.PyAudio', mock)
def test_for_smoke_with_mode_std():
    config = [{Sound.CONF_PATH: ding_sound, Sound.CONF_MODE: Sound.MODE_STD}]
    dut = Sound(name='pytest', wav_files=config, cool_down=0)

    events = []
    def callback(sender, payload):
        events.append(payload)

    runner = make_runner(dut, callback)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        with start_runner(runner):
            time.sleep(0.5)
