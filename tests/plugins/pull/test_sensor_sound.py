import os
import time
import warnings

import pytest
from mock import patch

from pnp.mocking import PyAudioMock
from pnp.plugins.pull.sensor import Sound
from pnp.shared.sound import MODE_PEARSON, MODE_STD
from tests.conftest import resource_path
from . import start_runner, make_runner

DING_FILE_NAME = 'ding'
DING_SOUND = os.path.join(resource_path('sounds'), DING_FILE_NAME + '.wav')
MOCK = PyAudioMock(DING_SOUND)


def _package_installed():
    try:
        import pyaudio
        import numpy
        import scipy
        return True
    except ImportError:
        return False


@pytest.mark.asyncio
@pytest.mark.skipif(not _package_installed(), reason="requires package pyaudio, numpy, scipy")
async def test_for_smoke_with_mode_pearson():
    config = [{Sound.WavConfigSchema.CONF_PATH: DING_SOUND}]
    dut = Sound(name='pytest', wav_files=config)

    events = []
    def callback(sender, payload):
        events.append(payload)

    with patch('pyaudio.PyAudio', MOCK):
        runner = await make_runner(dut, callback)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            async with start_runner(runner):
                time.sleep(1)

    assert len(events) >= 1
    item = events[0]
    assert set(item.keys()) == {'type', 'sound', 'corrcoef', 'threshold'}


@pytest.mark.skipif(not _package_installed(), reason="requires package pyaudio, numpy, scipy")
@patch('pyaudio.PyAudio', MOCK)
def test_minimal_wav_file_config():
    config = [
        {Sound.WavConfigSchema.CONF_PATH: DING_SOUND}
    ]
    dut = Sound(name='pytest', wav_files=config)

    assert len(dut.wav_files) == 1
    wav_file = dut.wav_files[0]
    assert wav_file.wav_file.abs_path == DING_SOUND
    assert wav_file.wav_file.file_name == DING_FILE_NAME
    assert wav_file.cooldown_event is False
    assert wav_file.offset == 0.0
    assert wav_file.cooldown_period == 10
    assert wav_file.mode == MODE_PEARSON


@pytest.mark.skipif(not _package_installed(), reason="requires package pyaudio, numpy, scipy")
@patch('pyaudio.PyAudio', MOCK)
def test_minimal_wav_file_config():
    config = [
        {Sound.WavConfigSchema.CONF_PATH: DING_SOUND}
    ]
    dut = Sound(name='pytest', wav_files=config)

    assert len(dut.wav_files) == 1
    wav_file = dut.wav_files[0]
    assert wav_file.wav_file.abs_path == DING_SOUND
    assert wav_file.wav_file.file_name == DING_FILE_NAME
    assert wav_file.cooldown_event is False
    assert wav_file.offset == 0.0
    assert wav_file.cooldown_period == 10
    assert wav_file.mode == MODE_PEARSON


@pytest.mark.skipif(not _package_installed(), reason="requires package pyaudio, numpy, scipy")
@patch('pyaudio.PyAudio', MOCK)
def test_full_wav_file_config():
    config = [
        {
            Sound.WavConfigSchema.CONF_PATH: DING_SOUND,
            Sound.WavConfigSchema.CONF_COOLDOWN: {
                Sound.WavConfigSchema.CONF_COOLDOWN_EVENT: True,
                Sound.WavConfigSchema.CONF_COOLDOWN_PERIOD: "1m"
            },
            Sound.WavConfigSchema.CONF_MODE: MODE_STD,
            Sound.WavConfigSchema.CONF_OFFSET: 0.3
        }
    ]
    dut = Sound(name='pytest', wav_files=config)

    assert len(dut.wav_files) == 1
    wav_file = dut.wav_files[0]
    assert wav_file.wav_file.abs_path == DING_SOUND
    assert wav_file.wav_file.file_name == DING_FILE_NAME
    assert wav_file.cooldown_event is True
    assert wav_file.offset == 0.3
    assert wav_file.cooldown_period == 60
    assert wav_file.mode == MODE_STD
