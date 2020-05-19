import asyncio
import socket

import aiohttp
import pytest
from aiohttp import ContentTypeError

from pnp.api import create_api, run_api_background


def get_free_tcp_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    addr, port = tcp.getsockname()
    tcp.close()
    return port


async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            try:
                return response.status, await response.json()
            except ContentTypeError:
                return response.status, await response.text()


@pytest.mark.asyncio
async def test_health():
    port = get_free_tcp_port()
    api = create_api(enable_metrics=False, enable_swagger=False)
    server = run_api_background(api, port)
    await asyncio.sleep(0.25)  # Wait for the server to startup
    try:
        url = 'http://127.0.0.1:{}/health'.format(port)
        status, json_ = await fetch(url)

        assert status == 200
        assert json_ == {'success': True}
    finally:
        server.close()


@pytest.mark.asyncio
async def test_swagger():
    port = get_free_tcp_port()
    api = create_api(enable_metrics=False, enable_swagger=True)
    server = run_api_background(api, port)
    await asyncio.sleep(0.25)  # Wait for the server to startup
    try:
        url = 'http://127.0.0.1:{}/swagger'.format(port)
        status, json_ = await fetch(url)

        assert status == 200
    finally:
        server.close()
