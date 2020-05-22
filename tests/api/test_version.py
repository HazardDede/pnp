import pytest

from tests.conftest import api_get, api_start


@pytest.mark.asyncio
async def test_endpoint():
    async with api_start() as api:
        url = 'http://127.0.0.1:{}/version'.format(api.port)
        status, json_ = await api_get(url)

        from pnp import __version__
        assert status == 200
        assert json_['version'] == __version__
