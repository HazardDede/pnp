import asyncio

import pytest

from pnp.api import create_api, run_api_background
from tests.api.helper import get_free_tcp_port, get


@pytest.mark.asyncio
async def test_endpoint():
    port = get_free_tcp_port()
    api = create_api(enable_metrics=False, enable_swagger=False)
    server = run_api_background(api, port)
    await asyncio.sleep(0.25)  # Wait for the server to startup
    try:
        url = 'http://127.0.0.1:{}/health'.format(port)
        status, json_ = await get(url)

        assert status == 200
        assert json_ == {'success': True}
    finally:
        server.close()
