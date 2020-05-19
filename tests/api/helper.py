import socket

import aiohttp
from aiohttp import ContentTypeError


def get_free_tcp_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    addr, port = tcp.getsockname()
    tcp.close()
    return port


async def get(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            try:
                return response.status, await response.json()
            except ContentTypeError:
                return response.status, await response.text()


async def post(url):
    async with aiohttp.ClientSession() as session:
        async with session.post(url) as response:
            try:
                return response.status, await response.json()
            except ContentTypeError:
                return response.status, await response.text()