import logging

import pytest

from tests.conftest import api_start, api_post


@pytest.mark.asyncio
async def test_endpoint():
    async with api_start() as api:
        url = 'http://127.0.0.1:{}/loglevel?level=ERROR'.format(api.port)
        status, json_ = await api_post(url)

        assert status == 200
        assert json_ == {}
        assert logging.getLogger().level == logging.ERROR

        url = 'http://127.0.0.1:{}/loglevel?level=INFO'.format(api.port)
        status, json_ = await api_post(url)

        assert status == 200
        assert json_ == {}
        assert logging.getLogger().level == logging.INFO


@pytest.mark.asyncio
async def test_endpoint_no_log_level():
    async with api_start() as api:
        url = 'http://127.0.0.1:{}/loglevel'.format(api.port)
        status, json_ = await api_post(url)

        assert status == 400
        assert list(json_.keys()) == ['message']
        assert json_['message'] == "Argument 'level' in query string not set."


@pytest.mark.asyncio
async def test_endpoint_unknown_log_level():
    async with api_start() as api:
        url = 'http://127.0.0.1:{}/loglevel?level=UNKNOWN'.format(api.port)
        status, json_ = await api_post(url)

        assert status == 400
        assert list(json_.keys()) == ['message']
        assert json_['message'] == "Argument 'level' is not a valid logging level."
