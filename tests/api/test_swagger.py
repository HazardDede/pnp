import pytest

from tests.conftest import api_start, api_get


@pytest.mark.asyncio
async def test_endpoint():
    async with api_start(swagger=True) as api:
        url = 'http://127.0.0.1:{}/swagger'.format(api.port)
        status, json_ = await api_get(url)

        assert status == 200
