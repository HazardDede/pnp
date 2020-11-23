import pytest

from pnp.api.endpoints import Trigger
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
        Trigger(tasks).attach(api.fastapi)
        url = 'http://127.0.0.1:{}/trigger?task=pytest'.format(api.port)
        status, json_ = await api_post(url)

        assert status == 200
        assert json_ == {}
        assert result == [42]


@pytest.mark.asyncio
async def test_endpoint_no_task():
    async with api_start() as api:
        Trigger([]).attach(api.fastapi)
        url = 'http://127.0.0.1:{}/trigger'.format(api.port)
        status, json_ = await api_post(url)

        assert status == 422
        assert json_ == {
            'detail': [{
                'loc': ['query', 'task'],
                'msg': 'field required',
                'type': 'value_error.missing'
            }]
        }


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
        Trigger(tasks).attach(api.fastapi)
        url = 'http://127.0.0.1:{}/trigger?task=unknown'.format(api.port)
        status, json_ = await api_post(url)

        assert status == 422
        assert json_ == {'detail': "Given task name 'unknown' is not a known task."}


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
        Trigger(tasks).attach(api.fastapi)
        url = 'http://127.0.0.1:{}/trigger?task=pytest'.format(api.port)
        status, json_ = await api_post(url)

        assert status == 422
        assert json_ == {
            'detail': "Task 'pytest' does not support pull_now() / async_pull_now(). "
                      "Implement PullNowMixin / AsyncPullMixin for support"
        }


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
        Trigger(tasks).attach(api.fastapi)
        url = 'http://127.0.0.1:{}/trigger?task=pytest'.format(api.port)
        status, json_ = await api_post(url)

        assert status == 500
        assert json_ == {'detail': 'While triggering the poll an error occurred.'}
