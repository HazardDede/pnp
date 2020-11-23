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

        assert status == 422
        assert json_ == {
            'detail': [{
                'loc': ['query', 'level'],
                'msg': 'field required',
                'type': 'value_error.missing'
            }]
        }


@pytest.mark.asyncio
async def test_endpoint_unknown_log_level():
    async with api_start() as api:
        url = 'http://127.0.0.1:{}/loglevel?level=UNKNOWN'.format(api.port)
        status, json_ = await api_post(url)

        assert status == 422
        assert json_ == {
            'detail': [{
                'ctx': {
                    'pattern': '^DEBUG|INFO|WARNING|ERROR|CRITICAL$'
                },
                'loc': ['query', 'level'],
                'msg': 'string does not match regex '
                '"^DEBUG|INFO|WARNING|ERROR|CRITICAL$"',
                'type': 'value_error.str.regex'
            }]
        }
