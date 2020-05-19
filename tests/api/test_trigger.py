import asyncio

import pytest

from pnp.api import create_api, run_api_background, add_trigger_endpoint
from pnp.models import TaskModel, PullModel, PushModel
from pnp.plugins.push.simple import Nop
from tests.api.helper import get_free_tcp_port, post
from tests.dummies.polling import SyncPollingDummy, AsyncPollingDummy, NoPollingDummy, ErrorPollingDummy


@pytest.mark.asyncio
@pytest.mark.parametrize("clazz", [
    SyncPollingDummy,
    AsyncPollingDummy
])
async def test_endpoint_working(clazz):
    port = get_free_tcp_port()
    polling = clazz(name='pytest_pull')
    result = []
    polling.on_payload = lambda pull, payload: result.append(payload)
    tasks = {
        'pytest': TaskModel(
            name='pytest',
            pull=PullModel(instance=polling),
            pushes=[PushModel(instance=Nop(name='pytest_push'))]
        )
    }
    api = create_api(enable_metrics=False, enable_swagger=False)
    add_trigger_endpoint(api, tasks)
    server = run_api_background(api, port)
    await asyncio.sleep(0.25)  # Wait for the server to startup
    try:
        url = 'http://127.0.0.1:{}/trigger?task=pytest'.format(port)
        status, json_ = await post(url)

        assert status == 200
        assert json_ == {}
        assert result == [42]
    finally:
        server.close()


@pytest.mark.asyncio
async def test_endpoint_no_task():
    port = get_free_tcp_port()
    api = create_api(enable_metrics=False, enable_swagger=False)
    add_trigger_endpoint(api, {})
    server = run_api_background(api, port)
    await asyncio.sleep(0.25)  # Wait for the server to startup
    try:
        url = 'http://127.0.0.1:{}/trigger'.format(port)
        status, json_ = await post(url)

        assert status == 400
        assert list(json_.keys()) == ['message']
        assert json_['message'] == "Argument 'task' in query string not set."
    finally:
        server.close()


@pytest.mark.asyncio
async def test_endpoint_unknown_task():
    port = get_free_tcp_port()
    tasks = {
        'pytest': TaskModel(
            name='pytest',
            pull=PullModel(instance=SyncPollingDummy(name='pytest_pull')),
            pushes=[PushModel(instance=Nop(name='pytest_push'))]
        )
    }
    api = create_api(enable_metrics=False, enable_swagger=False)
    add_trigger_endpoint(api, tasks)
    server = run_api_background(api, port)
    await asyncio.sleep(0.25)  # Wait for the server to startup
    try:
        url = 'http://127.0.0.1:{}/trigger?task=unknown'.format(port)
        status, json_ = await post(url)

        assert status == 400
        assert list(json_.keys()) == ['message']
        assert json_['message'] == "Value 'unknown' of argument 'task' is not a known task."
    finally:
        server.close()


@pytest.mark.asyncio
async def test_endpoint_not_a_poll():
    port = get_free_tcp_port()
    tasks = {
        'pytest': TaskModel(
            name='pytest',
            pull=PullModel(instance=NoPollingDummy(name='pytest_pull')),
            pushes=[PushModel(instance=Nop(name='pytest_push'))]
        )
    }
    api = create_api(enable_metrics=False, enable_swagger=False)
    add_trigger_endpoint(api, tasks)
    server = run_api_background(api, port)
    await asyncio.sleep(0.25)  # Wait for the server to startup
    try:
        url = 'http://127.0.0.1:{}/trigger?task=pytest'.format(port)
        status, json_ = await post(url)

        assert status == 400
        assert list(json_.keys()) == ['message']
        assert json_['message'] == "Can only trigger polling pulls, but pull instance of task 'pytest' is not a poll."
    finally:
        server.close()


@pytest.mark.asyncio
async def test_endpoint_polling_error():
    port = get_free_tcp_port()
    tasks = {
        'pytest': TaskModel(
            name='pytest',
            pull=PullModel(instance=ErrorPollingDummy(name='pytest_pull')),
            pushes=[PushModel(instance=Nop(name='pytest_push'))]
        )
    }
    api = create_api(enable_metrics=False, enable_swagger=False)
    add_trigger_endpoint(api, tasks)
    server = run_api_background(api, port)
    await asyncio.sleep(0.25)  # Wait for the server to startup
    try:
        url = 'http://127.0.0.1:{}/trigger?task=pytest'.format(port)
        status, json_ = await post(url)

        assert status == 500
        assert list(json_.keys()) == ['message']
        assert json_['message'] == "While triggering the poll an error occurred."
    finally:
        server.close()
