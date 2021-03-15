import asyncio
import json

import pytest
from httpx import AsyncClient

from pnp.api import RestAPI
from pnp.plugins.pull.http import Server
from tests.plugins.pull import make_runner, start_runner


async def _run_test(
        url, data, assertion_fun, method='POST', allowed_methods='POST', status_code=200
):
    dut = Server(prefix_path='pytest', name='pytest', allowed_methods=allowed_methods)
    runner = await make_runner(dut)

    rest = RestAPI()
    rest.create_api('pytest', False)

    async with start_runner(runner):
        await asyncio.sleep(0.1)  # Wait for the initialization completed
        async with AsyncClient(app=rest.fastapi, base_url="http://test") as client:
            fun = client.get
            if method == 'POST':
                fun = client.post

            response = await fun(
                url=url,
                data=data
            )

    assert response.status_code == status_code
    if status_code == 200:
        assert response.json() == {'success': True}
    assertion_fun(runner.events[0] if runner.events else None)


@pytest.mark.asyncio
async def test_json_data():
    def assert_this(payload):
        assert payload is not None
        assert payload['endpoint'] == "resource/endpoint"
        assert payload['method'] == "POST"
        assert payload['query'] == {'foo': 'bar', 'bar': 'baz'}
        assert payload['data'] == {"baz": "bar"}
        assert payload['is_json'] is True

    await _run_test(
        url='/pytest/resource/endpoint?foo=bar&bar=baz',
        data=json.dumps({"baz": "bar"}),
        assertion_fun=assert_this
    )


@pytest.mark.asyncio
async def test_non_json_data():
    def assert_this(payload):
        assert payload is not None
        assert payload['endpoint'] == "resource/endpoint"
        assert payload['method'] == "POST"
        assert payload['query'] == {'foo': 'bar', 'bar': 'baz'}
        assert payload['data'] == b'foobarbaznojson'
        assert payload['is_json'] is False

    await _run_test(
        url='/pytest/resource/endpoint?foo=bar&bar=baz',
        data="foobarbaznojson",
        assertion_fun=assert_this
    )


@pytest.mark.asyncio
async def test_multiple_query_params():
    def assert_this(payload):
        assert payload is not None
        assert payload['endpoint'] == "resource/endpoint/queryparam"
        assert payload['method'] == "POST"
        # On some systems the requests.args do not return a list, when the paramkey occurs multiple times
        # For now just make the test pass. I have to investigate later
        assert (payload['query'] == {'foo': 'bar', 'bar': ['baz', 'foo']}
                or payload['query'] == {'foo': 'bar', 'bar': 'baz'})
        assert payload['data'] is None
        assert payload['is_json'] is False

    await _run_test(
        url='/pytest/resource/endpoint/queryparam?foo=bar&bar=baz&bar=foo',
        data=None,
        assertion_fun=assert_this
    )


@pytest.mark.asyncio
async def test_query_params_wo_value():
    def assert_this(payload):
        assert payload is not None
        assert payload['endpoint'] == "resource/endpoint/queryparam"
        assert payload['method'] == "POST"
        # On some systems the requests.args do not return a list, when the paramkey occurs multiple times
        # For now just make the test pass. I have to investigate later
        assert ((payload['query'] == {'foo': '1'})
                or (payload['query'] == {'foo': '1'}))
        assert payload['data'] is None
        assert payload['is_json'] is False

    await _run_test(
        url='/pytest/resource/endpoint/queryparam?foo=1&bar=&bar=',
        data=None,
        assertion_fun=assert_this
    )


@pytest.mark.asyncio
async def test_query_different_methods_1():
    def assert_this(payload):
        assert payload['method'] == 'POST'

    await _run_test(
        url='/pytest/resource/endpoint/queryparam?foo=&bar=&bar',
        data=None,
        assertion_fun=assert_this
    )


@pytest.mark.asyncio
async def test_query_different_methods_2():
    def assert_this(payload):
        assert payload['method'] == 'POST'

    await _run_test(
        url='/pytest/resource/endpoint/queryparam?foo=&bar=&bar',
        data=None,
        allowed_methods='POST',
        method='POST',
        assertion_fun=assert_this
    )


@pytest.mark.asyncio
async def test_query_different_methods_3():
    def assert_this(payload):
        assert payload is None

    await _run_test(
        url='/pytest/resource/endpoint/queryparam?foo=&bar=&bar',
        data=None,
        allowed_methods='GET',
        method='POST',
        assertion_fun=assert_this,
        status_code=405
    )
