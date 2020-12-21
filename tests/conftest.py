import asyncio
import os
import socket

import aiohttp
from async_generator import asynccontextmanager, async_generator, yield_

from pnp.api import RestAPI


#
# Config related
#

def resource_path(path):
    return os.path.join(os.path.dirname(__file__), 'resources', path)


def path_to_config(config_name):
    return os.path.join(os.path.dirname(__file__), 'resources/configs', config_name)


#
# Web / Sockets
#

def get_free_tcp_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    addr, port = tcp.getsockname()
    tcp.close()
    return port


#
# API related
#

@asynccontextmanager
async def api_start(metrics=False):
    port = get_free_tcp_port()
    api = RestAPI()
    api.create_api('pytest', enable_metrics=metrics)
    async with api.run_api_background(port):
        # TODO: Check if we can connect to server or timeout
        await asyncio.sleep(1)  # Wait for the server to startup
        yield api
        await asyncio.sleep(0.5)


async def api_get(url, data=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, data=data) as response:
            try:
                return response.status, await response.json()
            except aiohttp.ContentTypeError:
                return response.status, await response.text()


async def api_post(url, data=None):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            try:
                return response.status, await response.json()
            except aiohttp.ContentTypeError:
                return response.status, await response.text()
