import json
import time
from threading import Thread

import asyncio
import websockets

import pnp.plugins.pull.hass as hass
from . import start_runner, make_runner


class WebSocketFakeServer:
    async def _handler(self, websocket, path):
        # First send that auth is required
        await websocket.send(json.dumps({'type': 'auth_required', 'ha_version': '0.88.2'}))

        auth_ok = False
        while not auth_ok:
            msg = json.loads(await websocket.recv())
            if msg.get('type', '') == 'auth' and msg.get('access_token', '') == 'abcdefg':
                auth_ok = True
                await websocket.send(json.dumps({'type': 'auth_ok'}))
            else:
                await websocket.send(json.dumps({'type': 'auth_invalid'}))

        event_data = [{
            'data': {
                'entity_id': 'light.lamp1',
                'old_state': {},
                'new_state': {}
            }
        }, {
            'data': {
                'entity_id': 'light.lamp2',
                'old_state': {},
                'new_state': {}
            }
        }]

        for i in range(10):
            await asyncio.sleep(0.05)
            await websocket.send(json.dumps({
                'type': 'event',
                'event': event_data[i % len(event_data)]
            }))

    def _loop(self):
        event_loop = asyncio.new_event_loop()
        self.loop = event_loop
        event_loop.run_until_complete(websockets.serve(self._handler, port=8123, loop=event_loop))
        event_loop.run_forever()

    def start(self):
        self._thr = Thread(target=self._loop)
        self._thr.start()

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)


def test_hass_state_for_smoke():
    fake = WebSocketFakeServer()
    fake.start()

    events = []
    def callback(plugin, payload):
        events.append(payload)

    dut = hass.State(name='pytest', url='ws://localhost:8123', token='abcdefg')
    runner = make_runner(dut, callback)
    with start_runner(runner):
        time.sleep(2)

    assert len(events) == 10

    fake.stop()
