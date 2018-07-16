import time
from datetime import datetime

import pytest
from mock import patch

from pnp.plugins.pull.mqtt import MQTTPull
from pnp.plugins.pull.http import Server
from pnp.plugins.pull.simple import Count, Repeat, CustomPolling
from .helper import make_runner, start_runner


@patch('paho.mqtt.client.Client')
@pytest.mark.parametrize("dut", [
    (Count(name='pytest', from_cnt=0, to_cnt=None, wait=10)),
    (Repeat(name='pytest', repeat='hello', wait=10)),
    (MQTTPull(name='pytest', host='youneverknow', topic='test/#', port=1883)),
    (CustomPolling(name='pytest', scheduled_callable=lambda: True, interval='1m')),
    # (Server(name='pytest'))
])
def test_pull_for_stopping_fast_with_high_wait(mqtt_client, dut):
    def callback(plugin, payload):
        pass

    runner = make_runner(dut, callback)
    start = datetime.now()
    with start_runner(runner):
        time.sleep(1)
    elapsed = datetime.now() - start

    assert elapsed.total_seconds() < 2.0
