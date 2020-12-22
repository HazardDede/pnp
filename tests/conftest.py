import os
import socket
from contextlib import contextmanager

from async_generator import asynccontextmanager
from httpx import AsyncClient
from starlette.testclient import TestClient

from pnp.api import RestAPI

#
# Config related
#
from pnp.api.endpoints import Endpoint


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

@contextmanager
def api_client(*endpoints: Endpoint) -> TestClient:
    rest = RestAPI()
    rest.create_api('pytest', False)
    for ep in endpoints:
        ep.attach(rest.fastapi)

    with TestClient(rest.fastapi) as testclient:
        yield testclient


@asynccontextmanager
async def api_client_async(*endpoints: Endpoint) -> AsyncClient:
    rest = RestAPI()
    rest.create_api('pytest', False)
    for ep in endpoints:
        ep.attach(rest.fastapi)

    async with AsyncClient(app=rest.fastapi, base_url="http://test") as testclient:
        yield testclient
