import os
import time
import warnings

import pytest
from mock import patch

from pnp.plugins.pull.sensor import Sound
from pnp.plugins.pull.sensor.sound import WavConfigSchema
from pnp.shared.sound import MODE_PEARSON, MODE_STD
from tests.conftest import resource_path
from tests.plugins.pull import make_runner, start_runner
from tests.plugins.pull.sensor.pyaudio_mock import PyAudioMock

DING_FILE_NAME = 'ding'
DING_SOUND = os.path.join(resource_path('sounds'), DING_FILE_NAME + '.wav')
MOCK = PyAudioMock(DING_SOUND)


@pytest.mark.asyncio
async def test_for_smoke_with_mode_pearson():
    config = [{WavConfigSchema.CONF_PATH: DING_SOUND}]
    dut = Sound(name='pytest', wav_files=config)

    with patch('pyaudio.PyAudio', MOCK):
        runner = await make_runner(dut)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            async with start_runner(runner):
                time.sleep(1)

    assert len(runner.events) >= 1
    item = runner.events[0]
    assert set(item.keys()) == {'type', 'sound', 'corrcoef', 'threshold'}


@patch('pyaudio.PyAudio', MOCK)
def test_minimal_wav_file_config():
    config = [
        {WavConfigSchema.CONF_PATH: DING_SOUND}
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


@patch('pyaudio.PyAudio', MOCK)
def test_minimal_wav_file_config():
    config = [
        {WavConfigSchema.CONF_PATH: DING_SOUND}
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


@patch('pyaudio.PyAudio', MOCK)
def test_full_wav_file_config():
    config = [
        {
            WavConfigSchema.CONF_PATH: DING_SOUND,
            WavConfigSchema.CONF_COOLDOWN: {
                WavConfigSchema.CONF_COOLDOWN_EVENT: True,
                WavConfigSchema.CONF_COOLDOWN_PERIOD: "1m"
            },
            WavConfigSchema.CONF_MODE: MODE_STD,
            WavConfigSchema.CONF_OFFSET: 0.3
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


# def test_repr():
#     config = [
#         {WavConfigSchema.CONF_PATH: DING_SOUND}
#     ]
#     dut = Sound(name='pytest', wav_files=config)
#     assert repr(dut) == "blah"
