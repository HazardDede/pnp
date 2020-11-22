import pytest

from tests.conftest import api_start, api_get


@pytest.mark.asyncio
async def test_endpoint():
    async with api_start() as api:
        url = 'http://127.0.0.1:{}/docs'.format(api.port)
        status, json_ = await api_get(url)

        assert status == 200
