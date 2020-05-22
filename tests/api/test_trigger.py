import pytest

from pnp.models import TaskModel, PullModel, PushModel
from pnp.plugins.push.simple import Nop
from tests.conftest import api_start, api_post
from tests.dummies.polling import SyncPollingDummy, AsyncPollingDummy, NoPollingDummy, ErrorPollingDummy


@pytest.mark.asyncio
@pytest.mark.parametrize("clazz", [
    SyncPollingDummy,
    AsyncPollingDummy
])
async def test_endpoint_working(clazz):
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
    async with api_start() as api:
        api.add_trigger_endpoint(tasks)
        url = 'http://127.0.0.1:{}/trigger?task=pytest'.format(api.port)
        status, json_ = await api_post(url)

        assert status == 200
        assert json_ == {}
        assert result == [42]


@pytest.mark.asyncio
async def test_endpoint_no_task():
    async with api_start() as api:
        api.add_trigger_endpoint({})
        url = 'http://127.0.0.1:{}/trigger'.format(api.port)
        status, json_ = await api_post(url)

        assert status == 400
        assert list(json_.keys()) == ['message']
        assert json_['message'] == "Argument 'task' in query string not set."


@pytest.mark.asyncio
async def test_endpoint_unknown_task():
    tasks = {
        'pytest': TaskModel(
            name='pytest',
            pull=PullModel(instance=SyncPollingDummy(name='pytest_pull')),
            pushes=[PushModel(instance=Nop(name='pytest_push'))]
        )
    }
    async with api_start() as api:
        api.add_trigger_endpoint(tasks)
        url = 'http://127.0.0.1:{}/trigger?task=unknown'.format(api.port)
        status, json_ = await api_post(url)

        assert status == 400
        assert list(json_.keys()) == ['message']
        assert json_['message'] == "Value 'unknown' of argument 'task' is not a known task."


@pytest.mark.asyncio
async def test_endpoint_not_a_poll():
    tasks = {
        'pytest': TaskModel(
            name='pytest',
            pull=PullModel(instance=NoPollingDummy(name='pytest_pull')),
            pushes=[PushModel(instance=Nop(name='pytest_push'))]
        )
    }
    async with api_start() as api:
        api.add_trigger_endpoint(tasks)
        url = 'http://127.0.0.1:{}/trigger?task=pytest'.format(api.port)
        status, json_ = await api_post(url)

        assert status == 400
        assert list(json_.keys()) == ['message']
        assert json_['message'] == "Can only trigger polling pulls, but pull instance of task 'pytest' is not a poll."


@pytest.mark.asyncio
async def test_endpoint_polling_error():
    tasks = {
        'pytest': TaskModel(
            name='pytest',
            pull=PullModel(instance=ErrorPollingDummy(name='pytest_pull')),
            pushes=[PushModel(instance=Nop(name='pytest_push'))]
        )
    }
    async with api_start() as api:
        api.add_trigger_endpoint(tasks)
        url = 'http://127.0.0.1:{}/trigger?task=pytest'.format(api.port)
        status, json_ = await api_post(url)

        assert status == 500
        assert list(json_.keys()) == ['message']
        assert json_['message'] == "While triggering the poll an error occurred."
