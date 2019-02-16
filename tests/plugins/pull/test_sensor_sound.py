import os
import time

import warnings
from mock import patch

from pnp.mocking import PyAudioMock
from pnp.plugins.pull.sensor import Sound
from tests.conftest import resource_path
from tests.plugins.helper import start_runner, make_runner


ding_sound = os.path.join(resource_path('sounds'), 'ding.wav')
mock = PyAudioMock(ding_sound)


@patch('pyaudio.PyAudio', mock)
def test_for_smoke():
    dut = Sound(name='pytest', wav_file=ding_sound, cool_down=0)

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
